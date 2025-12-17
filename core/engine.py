import json
from pathlib import Path
from core.dictionary_store import DictionaryStore
from core.trq_graph import TRQGraph
from core.intent_parser import parse_intent
from core.templates import (
    resposta_definicao, resposta_nao_encontrei, resposta_como, resposta_porque,
    resposta_lista, resposta_ensinar_ok, resposta_ensinar_uso,
    resposta_saudacao, resposta_despedida, resposta_agradecimento, resposta_confirmacao,
    resposta_afirmacao, resposta_negacao
)
from core.session_store import get_session
from core.profiles import PROFILES
from core.tsmp import Candidate, select_top
from core.tokenizer import normalize, tokenize
from core.dialogue_state import EstadoDialogo, InferenciaPragmatica

# Controle do verbalizador RWKV (desligável a qualquer momento)
# Implementação local de resposta_exemplo caso não esteja disponível em core.templates
def resposta_exemplo(subject: str, exemplos):
    if not exemplos:
        return f"Não encontrei exemplos para '{subject}'."
    if isinstance(exemplos, (list, tuple)):
        exemplos_fmt = "; ".join(str(e) for e in exemplos)
    else:
        exemplos_fmt = str(exemplos)
    return f"Exemplos de {subject}: {exemplos_fmt}"

USE_VERBALIZER = True

try:
    from core.verbalizer_rwkv import RWKVVerbalizer
except Exception:
    RWKVVerbalizer = None

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class Antonia:
    def __init__(self):
        self.dict_store = DictionaryStore(str(DATA_DIR / "dictionary_pt.json"))
        self.kb_path = DATA_DIR / "knowledge_base.json"
        self.kb = self._load_kb()
        
        # Grafo TRQ - malha explícita de conceitos e relações
        self.graph = TRQGraph(str(DATA_DIR / "trq_graph.json"))
        
        # Estado conversacional (um por sessão)
        # Mapeia session_id -> EstadoDialogo
        self.estados_dialogo = {}
        
        # Verbalizador RWKV opcional
        self.verbalizer = None
        if USE_VERBALIZER and RWKVVerbalizer:
            try:
                self.verbalizer = RWKVVerbalizer(
                    model_path=str(DATA_DIR.parent / "models" / "RWKV-5-World-3B-v2-20231113-ctx4096.pth"),
                    strategy="cpu fp32"
                )
                print("[Antonia] Verbalizador RWKV carregado.")
            except Exception as e:
                print(f"[Antonia] Verbalizador RWKV não disponível: {e}")
                self.verbalizer = None
        elif USE_VERBALIZER:
            print("[Antonia] Verbalizador RWKV não disponível: módulo ausente.")

    def _load_kb(self):
        if self.kb_path.exists():
            return json.loads(self.kb_path.read_text(encoding="utf-8"))
        return {"listas": {}, "notas": []}

    def _resolve_followup_subject(self, intent, estado):
        """
        Se a pergunta for um follow-up (ex.: "e como funciona?"), usa o tópico atual.
        """
        subj = (intent.subject or "").strip()
        if subj:
            return subj
        if intent.kind in {"como", "porque", "exemplo", "definicao", "explicacao", "listar"}:
            topico = (estado.topico_atual or "").strip()
            if topico:
                return topico.split(" ")[0]
        return subj

    def _build_candidates(self, session_id: str, prof, metadata, estado, intent):
        sess = get_session(session_id)
        if not sess:
            raise ValueError("sessao_invalida")

        subject = (intent.subject or "").strip()

        cands = []
        fontes = prof.tsmp.fontes_permitidas

        # Follow-up: "como funciona?" -> usa o tópico atual, se existir
        if intent.kind in {"como","porque","exemplo"} and not subject:
            subject = (estado.topico_atual or "").strip().split(" ")[0]
            if subject:
                entry = self.dict_store.lookup(subject)
                if entry:
                    forma = entry.get("forma") or subject
                    cands.append(Candidate(
                        source="dictionary",
                        text=f"{forma} ({entry.get('classe','')}): {entry.get('definicao','')}",
                        base_weight=0.85,
                        meta={"word": subject}
                    ))

        if "*" in fontes or "kb" in fontes:
            for n in self.kb.get("notas", [])[-30:]:
                cands.append(Candidate("kb", n, 0.55, {}))

            subj = (intent.subject or "").strip()
            if subj and subj in self.kb.get("listas", {}):
                itens = self.kb["listas"][subj]
                cands.append(Candidate("kb", f"lista:{subj} -> {', '.join(itens[:20])}", 0.60, {"list": subj}))

        if ("*" in fontes or "episodic" in fontes) and not metadata.get("modo_trq_duro"):
            for m in sess.episodic_memory[-20:]:
                cands.append(Candidate("episodic", f"{m['role']}: {m['text']}", 0.35, {}))

        if "*" in fontes or "subsignals" in fontes:
            st = metadata.get("estado")
            rs = metadata.get("ressonancia")
            cands.append(Candidate("subsignals", f"estado={st} ressonancia={rs}", 0.40, {}))

        return cands

    def answer(self, user_text: str, session_id: str) -> str:
        sess = get_session(session_id)
        if not sess:
            return "Sessão inválida."
        
        # Obtém ou cria estado de diálogo para esta sessão
        if session_id not in self.estados_dialogo:
            self.estados_dialogo[session_id] = EstadoDialogo()
        estado = self.estados_dialogo[session_id]

        prof = PROFILES[sess.profile_id]
        metadata = dict(prof.estado_base)
        metadata.update(sess.estado_dinamico)
        metadata["modo_trq_duro"] = prof.tsmp.modo_trq_duro
        metadata["show_subsignals"] = (prof.id == "debug")

        intent = parse_intent(user_text)

        # Fala social: nao passa por dicionario nem TSMP (fluidez > enciclopedia).
        if intent.kind == "saudacao":
            resp = resposta_saudacao()
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=None)
            return resp
        if intent.kind == "despedida":
            resp = resposta_despedida()
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=None)
            return resp
        if intent.kind == "agradecimento":
            resp = resposta_agradecimento()
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=None)
            return resp
        if intent.kind == "confirmacao":
            resp = resposta_confirmacao(estado.topico_atual)
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=estado.topico_atual)
            return resp
        if intent.kind == "afirmacao":
            resp = resposta_afirmacao(estado.topico_atual)
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=estado.topico_atual)
            return resp
        if intent.kind == "negacao":
            resp = resposta_negacao(estado.topico_atual)
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=estado.topico_atual)
            return resp

        # Resolve follow-ups ("e como funciona?") usando o tópico atual
        intent.subject = self._resolve_followup_subject(intent, estado)
        
        # Inferência pragmática (detecta tipo de pergunta)
        tipo_pergunta = InferenciaPragmatica.detectar_tipo_pergunta(user_text)

        if intent.kind == "ensinar":
            ok, msg = self._handle_add(intent.payload)
            resp = msg
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=None)
            return resp
        
        if intent.kind == "relacionar":
            resp = self._handle_relacionar(intent.payload)
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=None)
            return resp
        
        if intent.kind == "graph_cmd":
            resp = self._handle_graph_cmd(intent.payload)
            self._remember(sess, user_text, resp)
            estado.registrar_turno(user_text, resp, topico=None)
            return resp

        # Freio: mensagens muito curtas nao devem acionar TSMP (evita "assunto aleatorio")
        # e ajuda com termos compostos digitados sem "o que e ...".
        short_toks = tokenize(user_text or "")
        if intent.kind == "desconhecida" and len(short_toks) <= 2:
            intent.kind = "definicao"
            intent.subject = (user_text or "").strip()
            estado.papel = estado.inferir_papel(intent.subject)
            resp = self._respond_with_role(intent, ctx="", estado=estado, tipo_pergunta=tipo_pergunta, profile_id=prof.id)

            if self.verbalizer and prof.id != "trq_duro":
                try:
                    resp = self.verbalizer.verbalize(
                        base_content=resp,
                        tom=prof.prompt.tom,
                        max_tokens=120
                    )
                except Exception:
                    pass

            gesto = estado.gerar_gesto_final()
            if gesto:
                resp += gesto

            if prof.id == "debug":
                resp += "\n\n[DEBUG: TSMP pulado por entrada curta]"
                resp += f"\n[ESTADO: {estado}]"

            estado.registrar_turno(user_text, resp, topico=intent.subject)
            self._remember(sess, user_text, resp)
            return resp

        cands = self._build_candidates(session_id, prof, metadata, estado, intent)
        ctx, scored = select_top(cands, user_text, metadata, prof.tsmp.top_k, prof.tsmp.max_chars)

        # Atualiza papel conversacional baseado em contexto
        if intent.kind in {"definicao","explicacao","como","porque","listar","exemplo"} and intent.subject:
            conceito = intent.subject
        else:
            conceito = None
        estado.papel = estado.inferir_papel(conceito)
        
        # Gera resposta com consciência de papel
        resp = self._respond_with_role(intent, ctx, estado, tipo_pergunta, prof.id)
        
        # Verbalização opcional (RWKV só reescreve)
        if self.verbalizer and prof.id != "trq_duro":
            try:
                resp = self.verbalizer.verbalize(
                    base_content=resp,
                    tom=prof.prompt.tom,
                    max_tokens=120
                )
            except Exception:
                pass  # falha silenciosa: Antonia responde crua
        
        # Adiciona gesto conversacional (se contexto permitir)
        gesto = estado.gerar_gesto_final()
        if gesto:
            resp += gesto

        if prof.id == "debug":
            top_dbg = "\n".join([f"{i+1}. score={s:.3f} src={c.source} :: {c.text[:120]}"
                                 for i, (s, c) in enumerate(scored[:8])])
            resp = resp + f"\n\n[DEBUG: seleção TSMP]\n{top_dbg}"
            resp += f"\n[ESTADO: {estado}]"
        
        # Registra turno no estado de diálogo
        estado.registrar_turno(user_text, resp, topico=conceito)
        self._remember(sess, user_text, resp)
        return resp

    def _remember(self, sess, user_text: str, resp: str):
        sess.episodic_memory.append({"role": "user", "text": user_text})
        sess.episodic_memory.append({"role": "antonia", "text": resp})
        sess.episodic_memory = sess.episodic_memory[-80:]

    def _handle_add(self, payload: str):
        if not payload:
            return False, resposta_ensinar_uso()

        parts = [p.strip() for p in payload.split("|")]
        if len(parts) < 3:
            return False, resposta_ensinar_uso()

        palavra, classe, definicao = parts[0], parts[1], parts[2]
        relacoes = []
        if len(parts) >= 4 and parts[3]:
            relacoes = [normalize(x) for x in parts[3].split(",") if x.strip()]

        if not palavra or not classe or not definicao:
            return False, resposta_ensinar_uso()

        self.dict_store.add(palavra, classe, definicao, relacoes)
        
        # Adiciona nó ao grafo TRQ também
        self.graph.add_node(
            node_id=normalize(palavra),
            definicao=definicao,
            regiao="geral:humano:1",  # formato: nome:campo:nivel
            origem="humano",
            peso_estabilidade=1.0,  # Máxima estabilidade (entrada humana)
            peso_confianca=1.0       # Máxima confiança (entrada humana)
        )
        
        return True, resposta_ensinar_ok(palavra)
    
    def _handle_relacionar(self, payload: str) -> str:
        """
        Cria relação no grafo TRQ.
        Formato: /relacionar conceito1 | conceito2 | tipo
        Tipos válidos: definicao, parte_de, causa, relacionado, exemplo
        """
        if not payload:
            return "Uso: /relacionar conceito1 | conceito2 | tipo\nTipos: definicao, parte_de, causa, relacionado, exemplo"
        
        parts = [p.strip() for p in payload.split("|")]
        if len(parts) < 3:
            return "Uso: /relacionar conceito1 | conceito2 | tipo"
        
        conceito1 = normalize(parts[0])
        conceito2 = normalize(parts[1])
        tipo = parts[2].lower()
        
        if tipo not in self.graph.TIPOS_VALIDOS:
            return f"Tipo inválido. Use: {', '.join(self.graph.TIPOS_VALIDOS)}"
        
        # Verifica se ambos os nós existem
        if not self.graph.get_node(conceito1):
            return f"Conceito '{conceito1}' não existe no grafo. Use /add primeiro."
        
        if not self.graph.get_node(conceito2):
            return f"Conceito '{conceito2}' não existe no grafo. Use /add primeiro."
        
        ok = self.graph.add_edge(conceito1, conceito2, tipo)
        if ok:
            return f"Relação criada: {conceito1} → {conceito2} ({tipo})"
        return "Erro ao criar relação."
    
    def _handle_graph_cmd(self, payload: str) -> str:
        """
        Comandos do grafo TRQ.
        /graph stats - estatísticas
        /graph ver conceito - ver nó e vizinhos
        """
        cmd = payload.strip().lower()
        
        if cmd == "stats":
            stats = self.graph.stats()
            return (
                f"Grafo TRQ:\n"
                f"- Nós: {stats['total_nodos']}\n"
                f"- Relações: {stats['total_arestas']}\n"
                f"- Regiões: {', '.join(stats['regioes']) if stats['regioes'] else 'nenhuma'}\n"
                f"- Tipos usados: {', '.join(stats['tipos_relacao']) if stats['tipos_relacao'] else 'nenhum'}"
            )
        
        if cmd.startswith("ver "):
            conceito = normalize(cmd[4:].strip())
            node = self.graph.get_node(conceito)
            if not node:
                return f"Conceito '{conceito}' não existe no grafo."
            
            vizinhos = self.graph.neighbors(conceito)
            relacoes = []
            for v in vizinhos:
                rels = self.graph.related(conceito, v)
                for r in rels:
                    relacoes.append(f"  → {r['para']} ({r['tipo']})" if r['de'] == conceito else f"  ← {r['de']} ({r['tipo']})")
            
            resp = f"Nó: {node['id']}\n"
            resp += f"Definição: {node['definicao_curta']}\n"
            resp += f"Região: {node['regiao']}\n"
            if relacoes:
                resp += "Relações:\n" + "\n".join(relacoes)
            else:
                resp += "Sem relações."
            return resp
        
        return "Comandos: /graph stats | /graph ver <conceito>"

    def _respond_with_role(self, intent, ctx: str, estado: EstadoDialogo, tipo_pergunta: str, profile_id: str) -> str:
        """
        Responde com consciência de papel conversacional.
        
        NÃO inventa conteúdo. Adapta FORMA baseado em:
        - papel atual (definidora, explicadora, exploradora)
        - tipo de pergunta (pragmática)
        - profundidade no tópico
        """
        subject = (intent.subject or "").strip()
        clean_term = lambda s: (s or "").strip().strip("\"'").rstrip("?!.,;:")

        # Follow-up: "como funciona?" -> usa o tópico atual, se existir
        if intent.kind in {"como","porque","exemplo"} and not subject:
            subject = (estado.topico_atual or "").strip()
        head_tokens = tokenize(subject) if subject else []
        head = head_tokens[0] if head_tokens else (subject.split(" ")[0] if subject else "")

        # Regra de saudação básica (ato fundador da conversa)
        if intent.kind == "desconhecida" and head in {"oi", "ola", "olá"}:
            return "Oi. Como posso te ajudar?"

        if intent.kind in {"localizacao", "camada"}:
            alvo = clean_term(subject or head)
            if not alvo:
                return "Qual conceito voce quer localizar (ex: TCP, IP, kernel)?"

            q = (intent.payload or "")
            alvo_norm = normalize(alvo)
            if alvo_norm == "tcp" and ("osi" in q or "tcp ip" in q or "tcp-ip" in q):
                return "TCP fica na Camada de Transporte (L4) do modelo OSI e na Camada de Transporte do modelo TCP/IP."
            if alvo_norm == "udp" and ("osi" in q or "tcp ip" in q or "tcp-ip" in q):
                return "UDP fica na Camada de Transporte (L4) do modelo OSI e na Camada de Transporte do modelo TCP/IP."
            if alvo_norm == "ip" and ("osi" in q or "tcp ip" in q or "tcp-ip" in q):
                return "IP fica na Camada de Rede (L3) do modelo OSI e na Camada Internet do modelo TCP/IP."

            entry = self.dict_store.lookup(alvo)
            if entry:
                forma = entry.get("forma") or alvo
                resp = resposta_definicao(forma, entry.get("definicao", ""), entry.get("classe"))
                resp += self._expandir_com_grafo(normalize(alvo), "explicadora")
                return resp

            node = self.graph.get_node(normalize(alvo))
            if node:
                resp = f"{node['id']}: {node['definicao_curta']}"
                resp += self._expandir_com_grafo(normalize(alvo), "explicadora")
                return resp

            if profile_id == "trq_duro":
                return resposta_nao_encontrei(alvo)
            return (
                f"Eu entendi que voce quer saber onde **{alvo}** se encaixa.\n"
                "Me diga o contexto (ex: modelo OSI/TCP-IP, ou em qual area) e eu respondo de forma direta.\n"
                "Se quiser me ensinar: /add palavra | classe | definicao"
            )

        if intent.kind == "definicao":
            alvo = clean_term(subject or head)
            if not alvo:
                return "Diga a palavra que você quer definir."

            lookup_key = alvo
            entry = self.dict_store.lookup(lookup_key)
            conceito_id = normalize(lookup_key)
            if not entry and head and head != lookup_key:
                entry = self.dict_store.lookup(head)
                lookup_key = head
                conceito_id = normalize(head)

            if not entry:
                if profile_id == "trq_duro":
                    return resposta_nao_encontrei(alvo)
                return (
                    f"Ainda não tenho o verbete de **{alvo}**.\n"
                    "Me diga em 1 frase o contexto (onde voce viu/usa isso).\n"
                    "Se quiser, eu posso: (1) definicao curta (2) exemplos.\n"
                    f"Para ensinar: /add {alvo} | substantivo | <definicao>"
                )

            forma = entry.get("forma") or lookup_key
            resp_base = resposta_definicao(forma, entry.get("definicao",""), entry.get("classe"))
            
            # Se papel é explicadora/exploradora, expande com grafo
            if estado.papel in ["explicadora", "exploradora"]:
                resp_base += self._expandir_com_grafo(conceito_id, estado.papel)
            
            return resp_base

        if intent.kind == "listar":
            itens = self.kb.get("listas", {}).get(subject, [])
            return resposta_lista(subject, itens)
        
        if intent.kind == "explicacao":
            # "Fale sobre X", "explique X" - sempre expande (modo explicadora)
            if not (subject or head):
                return "Sobre o que você quer que eu fale?"

            alvo = clean_term(subject or head)
            lookup_key = alvo
            entry = self.dict_store.lookup(lookup_key)
            conceito_id = normalize(lookup_key)

            if not entry:
                # Tenta buscar no grafo pelo sujeito completo primeiro (termo composto)
                node = self.graph.get_node(conceito_id)
                if node:
                    resp = f"{node['id']}: {node['definicao_curta']}"
                    resp += self._expandir_com_grafo(conceito_id, "explicadora")
                    return resp

                # Fallback: tenta no head
                if head and head != lookup_key:
                    entry = self.dict_store.lookup(head)
                    lookup_key = head
                    conceito_id = normalize(head)
                    if not entry:
                        node = self.graph.get_node(conceito_id)
                        if node:
                            resp = f"{node['id']}: {node['definicao_curta']}"
                            resp += self._expandir_com_grafo(conceito_id, "explicadora")
                            return resp

                if profile_id == "trq_duro":
                    return resposta_nao_encontrei(alvo)
                return (
                    f"Ainda não tenho o verbete de **{alvo}**.\n"
                    "Me diga em 1 frase o contexto e eu tento explicar sem inventar.\n"
                    "Se preferir, voce pode me ensinar: /add palavra | classe | definicao"
                )

            forma = entry.get("forma") or lookup_key
            resp = resposta_definicao(forma, entry.get("definicao",""), entry.get("classe"))
            
            # Explicação SEMPRE expande (não depende de papel)
            resp += self._expandir_com_grafo(conceito_id, "explicadora")
            
            return resp

        if intent.kind == "exemplo":
            if not subject:
                return "Exemplo de quê? Me diga o conceito (ou continue no mesmo tema para eu manter o tópico)."
            exemplos = self._buscar_exemplos(subject)
            return resposta_exemplo(subject, exemplos)

        if intent.kind == "como":
            base = ctx if ctx else "eu ainda não tenho base suficiente no meu dicionário/conhecimento para detalhar."
            subj_out = subject or (estado.topico_atual or "isso")
            resp = resposta_como(subj_out, base)
            
            # Explicadora/exploradora expande com relações
            if estado.papel == "exploradora" and subject:
                resp += self._expandir_com_grafo(normalize(subject), "exploradora")
            
            return resp

        if intent.kind == "porque":
            base = ctx if ctx else "eu ainda não tenho base suficiente para justificar sem inventar."
            subj_out = subject or (estado.topico_atual or "isso")
            resp = resposta_porque(subj_out, base)
            
            # Exploradora busca causas no grafo
            if estado.papel == "exploradora" and subject:
                subject_norm = normalize(subject)
                causas = []
                for vizinho in self.graph.neighbors(subject_norm):
                    for e in self.graph.related(subject_norm, vizinho):
                        if e.get("tipo") == "causa" and e.get("de") == subject_norm:
                            causas.append(e)
                if causas:
                    resp += "\n\nRelações causais que conheço:\n"
                    for c in causas[:3]:
                        resp += f"- {c['de']} → {c['para']}\n"
            
            return resp

        if head:
            entry = self.dict_store.lookup(head)
            if entry:
                forma = entry.get("forma") or head
                resp = resposta_definicao(forma, entry.get("definicao",""), entry.get("classe"))
                
                # Expande se papel permitir
                if estado.papel in ["explicadora", "exploradora"]:
                    resp += self._expandir_com_grafo(normalize(head), estado.papel)
                
                return resp

        if ctx:
            return "Eu não identifiquei o tipo de pergunta, mas aqui está o que tenho de base:\n" + ctx
        return "Eu não tenho base suficiente ainda. Se você me der uma palavra-chave, eu tento definir."
    
    def _expandir_com_grafo(self, conceito_id: str, papel: str) -> str:
        """
        Expande resposta usando grafo TRQ.
        
        - explicadora: mostra vizinhos diretos
        - exploradora: navega 2 níveis, mostra padrões
        """
        node = self.graph.get_node(conceito_id)
        if not node:
            return ""
        
        vizinhos = self.graph.neighbors(conceito_id)
        if not vizinhos:
            return ""
        
        if papel == "explicadora":
            # Mostra relações diretas (1 nível)
            rels = []
            for v in vizinhos[:3]:  # Limita a 3 para não sobrecarregar
                edges = self.graph.related(conceito_id, v)
                for e in edges:
                    if e['de'] == conceito_id:
                        rels.append(f"- {e['tipo']}: {e['para']}")
            
            if rels:
                return "\n\nConexões diretas:\n" + "\n".join(rels)
        
        elif papel == "exploradora":
            # Explora 2 níveis, mostra estrutura
            rels = []
            for v in vizinhos[:5]:
                edges = self.graph.related(conceito_id, v)
                for e in edges:
                    if e['de'] == conceito_id:
                        rels.append(f"- {e['tipo']}: {e['para']}")
                        
                        # Segundo nível
                        vizinhos_2 = self.graph.neighbors(v)
                        if len(vizinhos_2) > 1:  # Tem mais conexões
                            rels.append(f"  └─ {e['para']} conecta a {len(vizinhos_2)-1} outros conceitos")
            
            if rels:
                return "\n\nEstrutura conceitual:\n" + "\n".join(rels[:8])  # Limita output
        
        return ""
    
    def _buscar_exemplos(self, subject: str):
        """
        Retorna exemplos associados a um conceito a partir do dicionário ou do grafo TRQ.
        """
        exemplos = []
        subject_norm = normalize(subject)
        
        # Procura exemplos no dicionário, se existirem
        entry = self.dict_store.lookup(subject_norm)
        if entry:
            ex = entry.get("exemplos") or entry.get("exemplo")
            if isinstance(ex, (list, tuple)):
                exemplos.extend(ex)
            elif ex:
                exemplos.append(ex)
        
        # Procura relações do tipo "exemplo" no grafo
        node = self.graph.get_node(subject_norm)
        if node:
            for vizinho in self.graph.neighbors(subject_norm):
                for e in self.graph.related(subject_norm, vizinho):
                    if e.get("tipo") == "exemplo" and e.get("de") == subject_norm:
                        exemplos.append(e.get("para"))
        
        # Remove duplicados preservando ordem
        vistos = set()
        dedup = []
        for ex in exemplos:
            if ex not in vistos:
                vistos.add(ex)
                dedup.append(ex)
        
        return dedup
