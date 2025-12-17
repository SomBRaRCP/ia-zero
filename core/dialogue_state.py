#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dialogue_state.py

Estado conversacional da Antonia.
NÃO é simulação de emoção - é CONTEXTO ESTRUTURAL.

Princípio guardião:
"Antonia não inventa. Não performa emoção.
Só fala além do literal quando houver CONTEXTO suficiente."
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from core.tokenizer import normalize

@dataclass
class Turno:
    """Um turno de conversa (pergunta/resposta)"""
    timestamp: str
    entrada: str
    saida: str
    topico: Optional[str] = None
    papel: str = "neutro"

class EstadoDialogo:
    """
    Estado conversacional vivo por sessão.
    
    NÃO armazena:
    - emoções simuladas
    - preferências inventadas
    - padrões de comportamento social
    
    ARMAZENA:
    - histórico factual de turnos
    - tópico em curso (se houver)
    - profundidade na área temática
    - papel funcional atual
    """
    
    # Papéis possíveis (funções, não personas)
    PAPEIS = {
        "neutro": "aguardando contexto",
        "definidora": "resposta objetiva e direta",
        "explicadora": "expande com relações do grafo",
        "exploradora": "conecta conceitos em profundidade"
    }
    
    def __init__(self):
        self.topico_atual: Optional[str] = None
        self.papel: str = "neutro"
        self.profundidade: int = 0
        self.historico: List[Turno] = []
        self.area_tematica: Optional[str] = None  # fisica, matematica, etc
    
    def registrar_turno(self, entrada: str, saida: str, topico: Optional[str] = None):
        """Registra um turno de conversa."""
        self.historico.append(Turno(
            timestamp=datetime.now().isoformat(),
            entrada=entrada,
            saida=saida,
            topico=topico,
            papel=self.papel
        ))
        
        # Atualiza estado
        if topico:
            if topico == self.topico_atual:
                self.profundidade += 1
            else:
                # Mudança de tópico
                self.topico_atual = topico
                self.profundidade = 1
                self.papel = "neutro"
    
    def inferir_papel(self, conceito: Optional[str] = None) -> str:
        """
        Infere papel funcional baseado em CONTEXTO ESTRUTURAL.
        
        Não adivinha psicologia. Lê sinais objetivos:
        - profundidade no tópico
        - tipo de pergunta
        - histórico recente
        """
        # Se está começando
        if self.profundidade == 0:
            return "neutro"
        
        # Se primeira pergunta sobre o conceito
        if self.profundidade == 1:
            return "definidora"
        
        # Se voltou ao mesmo conceito (interesse ativo)
        if self.profundidade == 2:
            return "explicadora"
        
        # Se está explorando profundamente
        if self.profundidade >= 3:
            return "exploradora"
        
        return "neutro"
    
    def precisa_continuar(self) -> bool:
        """
        Verifica se o contexto pede continuidade conversacional.
        
        NÃO é sobre "ser amigável".
        É sobre "há exploração em curso?".
        """
        # Se está explorando profundamente, há fluxo ativo
        return self.profundidade >= 2 and self.papel in ["explicadora", "exploradora"]
    
    def get_contexto_recente(self, n: int = 3) -> List[Turno]:
        """Retorna os N turnos mais recentes."""
        return self.historico[-n:] if len(self.historico) >= n else self.historico
    
    def reset_suave(self):
        """
        Reset suave - mantém área temática, zera profundidade.
        Usado quando muda conceito dentro da mesma área.
        """
        self.profundidade = 0
        self.papel = "neutro"
        self.topico_atual = None
    
    def reset_total(self):
        """
        Reset completo - limpa tudo.
        Usado ao começar nova sessão ou mudança radical de assunto.
        """
        self.topico_atual = None
        self.papel = "neutro"
        self.profundidade = 0
        self.area_tematica = None
        self.historico.clear()
    
    def gerar_gesto_final(self) -> str:
        """
        Gera gesto conversacional final - SE E SOMENTE SE houver contexto.
        
        NÃO gera:
        - se papel é "definidora" (resposta objetiva encerra)
        - se não há profundidade
        - se mudou de área temática
        
        GERA:
        - se está em exploração ativa
        - se há tópico estabelecido
        - APENAS como convite estrutural, não social
        """
        if not self.precisa_continuar():
            return ""
        
        if self.papel == "exploradora":
            # Convite baseado no grafo (não na sociabilidade)
            if self.topico_atual:
                return f"\n\nPosso explorar mais sobre {self.topico_atual} ou seguir para conceitos relacionados?"
            return "\n\nPosso expandir essas conexões ou mudar o foco?"
        
        if self.papel == "explicadora":
            return "\n\nQuer mais detalhes ou seguimos adiante?"
        
        return ""
    
    def __repr__(self) -> str:
        return (
            f"EstadoDialogo("
            f"topico={self.topico_atual}, "
            f"papel={self.papel}, "
            f"profundidade={self.profundidade}, "
            f"turnos={len(self.historico)})"
        )


class InferenciaPragmatica:
    """
    Inferência de intenção conversacional.
    
    NÃO é leitura de mente.
    É detecção de padrões ESTRUTURAIS na entrada.
    """
    
    @staticmethod
    def detectar_tipo_pergunta(texto: str) -> str:
        """
        Classifica tipo de pergunta por estrutura sintática.

        Não interpreta "sentimento". Lê FORMA.
        (Usa normalize() para alinhar com o parser de intent.)
        """
        t = normalize(texto or "")
        texto_lower = t.strip()

        # Pergunta de definição pura
        if texto_lower.startswith(("o que e", "qual e", "defina", "define")):
            return "definicao"

        # Pergunta de explicação (pede mais)
        if texto_lower.startswith(("como", "por que", "porque", "explica", "explique")):
            return "explicacao"

        # Pergunta de relação
        if ("relaciona" in texto_lower or "relacao" in texto_lower
            or "ligacao" in texto_lower or "conexao" in texto_lower):
            return "relacao"

        # Confirmação/exploração (continuação)
        if texto_lower.startswith(("e ", "mas ", "entao ")):
            return "continuacao"

        # Comando
        if not (texto or "").strip().endswith("?"):
            return "comando"

        return "neutra"
    
    @staticmethod
    def precisa_expansao(tipo_pergunta: str, estado: EstadoDialogo) -> bool:
        """
        Decide se a resposta deve ser expandida.
        
        Baseado em:
        - tipo estrutural da pergunta
        - profundidade no tópico
        - papel atual
        
        NÃO baseado em:
        - "vontade" de conversar
        - "educação" social
        """
        # Perguntas de definição pura não expandem (a menos que haja profundidade)
        if tipo_pergunta == "definicao" and estado.profundidade <= 1:
            return False
        
        # Perguntas de explicação pedem expansão
        if tipo_pergunta in ["explicacao", "relacao"]:
            return True
        
        # Continuação pede expansão se há contexto
        if tipo_pergunta == "continuacao" and estado.profundidade >= 1:
            return True
        
        # Comandos não expandem
        if tipo_pergunta == "comando":
            return False
        
        # Default: expande se há profundidade
        return estado.profundidade >= 2
