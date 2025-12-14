import json
from pathlib import Path
from core.dictionary_store import DictionaryStore
from core.intent_parser import parse_intent
from core.templates import (
    resposta_definicao, resposta_nao_encontrei, resposta_como, resposta_porque,
    resposta_lista, resposta_ensinar_ok, resposta_ensinar_uso
)
from core.session_store import get_session
from core.profiles import PROFILES
from core.tsmp import Candidate, select_top
from core.tokenizer import normalize

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class SofiaZero:
    def __init__(self):
        self.dict_store = DictionaryStore(str(DATA_DIR / "dictionary_pt.json"))
        self.kb_path = DATA_DIR / "knowledge_base.json"
        self.kb = self._load_kb()

    def _load_kb(self):
        if self.kb_path.exists():
            return json.loads(self.kb_path.read_text(encoding="utf-8"))
        return {"listas": {}, "notas": []}

    def _build_candidates(self, session_id: str, prof, metadata, intent):
        sess = get_session(session_id)
        if not sess:
            raise ValueError("sessao_invalida")

        cands = []
        fontes = prof.tsmp.fontes_permitidas

        if "*" in fontes or "dictionary" in fontes:
            subject = (intent.subject or "").strip().split(" ")[0]
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

        prof = PROFILES[sess.profile_id]
        metadata = dict(prof.estado_base)
        metadata.update(sess.estado_dinamico)
        metadata["modo_trq_duro"] = prof.tsmp.modo_trq_duro

        intent = parse_intent(user_text)

        if intent.kind == "ensinar":
            ok, msg = self._handle_add(intent.payload)
            resp = msg
            self._remember(sess, user_text, resp)
            return resp

        cands = self._build_candidates(session_id, prof, metadata, intent)
        ctx, scored = select_top(cands, user_text, metadata, prof.tsmp.top_k, prof.tsmp.max_chars)

        resp = self._respond_rule_based(intent, ctx)

        if prof.id == "debug":
            top_dbg = "\n".join([f"{i+1}. score={s:.3f} src={c.source} :: {c.text[:120]}"
                                 for i, (s, c) in enumerate(scored[:8])])
            resp = resp + "\n\n[DEBUG: seleção TSMP]\n" + top_dbg

        self._remember(sess, user_text, resp)
        return resp

    def _remember(self, sess, user_text: str, resp: str):
        sess.episodic_memory.append({"role": "user", "text": user_text})
        sess.episodic_memory.append({"role": "sofia", "text": resp})
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
        return True, resposta_ensinar_ok(palavra)

    def _respond_rule_based(self, intent, ctx: str) -> str:
        subject = (intent.subject or "").strip()
        head = subject.split(" ")[0] if subject else ""

        if intent.kind == "definicao":
            if not head:
                return "Diga a palavra que você quer definir."
            entry = self.dict_store.lookup(head)
            if not entry:
                return resposta_nao_encontrei(head)
            forma = entry.get("forma") or head
            return resposta_definicao(forma, entry.get("definicao",""), entry.get("classe"))

        if intent.kind == "listar":
            itens = self.kb.get("listas", {}).get(subject, [])
            return resposta_lista(subject, itens)

        if intent.kind == "como":
            base = ctx if ctx else "eu ainda não tenho base suficiente no meu dicionário/conhecimento para detalhar."
            return resposta_como(subject or "isso", base)

        if intent.kind == "porque":
            base = ctx if ctx else "eu ainda não tenho base suficiente para justificar sem inventar."
            return resposta_porque(subject or "isso", base)

        if head:
            entry = self.dict_store.lookup(head)
            if entry:
                forma = entry.get("forma") or head
                return resposta_definicao(forma, entry.get("definicao",""), entry.get("classe"))

        if ctx:
            return "Eu não identifiquei o tipo de pergunta, mas aqui está o que tenho de base:\n" + ctx
        return "Eu não tenho base suficiente ainda. Se você me der uma palavra-chave, eu tento definir."
