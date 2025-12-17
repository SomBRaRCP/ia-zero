#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bootstrap_knowledge.py

Popula Antonia com conhecimento fundamental.
Processo em 3 fases:

1. NÚCLEO: Conceitos científicos/filosóficos básicos (manual + validação)
2. MINERAÇÃO: DeepSeek extrai relações estruturadas
3. VALIDAÇÃO: Humano aprova/rejeita candidatos da quarentena

Princípio guardião:
"Antonia só aprende o que foi validado. Zero automação cega."
"""

from core.engine import Antonia
from core.session_store import create_session
from core.knowledge_miner import KnowledgeMiner
from pathlib import Path
import json

# =============================================================================
# FASE 1: NÚCLEO DE CONHECIMENTO
# =============================================================================

NUCLEO_CONCEITOS = {
    # FÍSICA
    "energia": {
        "classe": "substantivo",
        "definicao": "capacidade de realizar trabalho ou produzir mudanças",
        "relacoes": ["trabalho", "forca", "movimento"],
        "campo": "fisica"
    },
    "massa": {
        "classe": "substantivo",
        "definicao": "quantidade de matéria em um corpo",
        "relacoes": ["materia", "peso", "inercia"],
        "campo": "fisica"
    },
    "velocidade": {
        "classe": "substantivo",
        "definicao": "taxa de variação da posição em relação ao tempo",
        "relacoes": ["tempo", "espaco", "movimento"],
        "campo": "fisica"
    },
    
    # FILOSOFIA
    "filosofia": {
        "classe": "substantivo",
        "definicao": "estudo das questões fundamentais sobre existência, conhecimento, valores e razão",
        "relacoes": ["razao", "conhecimento", "verdade"],
        "campo": "filosofia"
    },
    "epistemologia": {
        "classe": "substantivo",
        "definicao": "ramo da filosofia que estuda a natureza, origem e limites do conhecimento",
        "relacoes": ["conhecimento", "verdade", "crenca"],
        "campo": "filosofia"
    },
    "etica": {
        "classe": "substantivo",
        "definicao": "ramo da filosofia que estuda a moralidade e os princípios do bem e do mal",
        "relacoes": ["moral", "valor", "dever"],
        "campo": "filosofia"
    },
    
    # MATEMÁTICA
    "numero": {
        "classe": "substantivo",
        "definicao": "entidade abstrata que representa quantidade ou ordem",
        "relacoes": ["quantidade", "medida", "contagem"],
        "campo": "matematica"
    },
    "conjunto": {
        "classe": "substantivo",
        "definicao": "coleção bem definida de objetos matemáticos",
        "relacoes": ["elemento", "pertinencia", "uniao"],
        "campo": "matematica"
    },
    
    # BIOLOGIA
    "celula": {
        "classe": "substantivo",
        "definicao": "unidade básica estrutural e funcional dos seres vivos",
        "relacoes": ["vida", "organismo", "membrana"],
        "campo": "biologia"
    },
    "dna": {
        "classe": "substantivo",
        "definicao": "molécula que carrega a informação genética dos seres vivos",
        "relacoes": ["gene", "heranca", "proteina"],
        "campo": "biologia"
    },
    
    # TEORIA FUNDAMENTAL
    "teoria": {
        "classe": "substantivo",
        "definicao": "conjunto organizado de princípios que explica fenômenos",
        "relacoes": ["hipotese", "explicacao", "modelo"],
        "campo": "ciencia"
    },
    "hipotese": {
        "classe": "substantivo",
        "definicao": "proposição testável que explica provisoriamente um fenômeno",
        "relacoes": ["teoria", "teste", "evidencia"],
        "campo": "ciencia"
    }
}

# Teorias famosas (para demonstrar que Antonia pode aprender)
TEORIAS_CONHECIDAS = {
    "relatividade": {
        "classe": "substantivo",
        "definicao": "teoria de Einstein que relaciona espaço, tempo, massa e energia",
        "relacoes": ["einstein", "espacotempo", "energia"],
        "campo": "fisica:moderna"
    },
    "evolucao": {
        "classe": "substantivo",
        "definicao": "teoria de Darwin sobre mudança das espécies ao longo do tempo",
        "relacoes": ["darwin", "selecao", "adaptacao"],
        "campo": "biologia"
    },
    "quantica": {
        "classe": "substantivo",
        "definicao": "teoria que descreve o comportamento de partículas subatômicas",
        "relacoes": ["particula", "onda", "probabilidade"],
        "campo": "fisica:moderna"
    }
}

# Filósofos importantes
FILOSOFOS = {
    "platao": {
        "classe": "substantivo",
        "definicao": "filósofo grego, discípulo de Sócrates, autor da Teoria das Ideias",
        "relacoes": ["filosofia", "idealismo", "socrates"],
        "campo": "filosofia:antiga"
    },
    "aristoteles": {
        "classe": "substantivo",
        "definicao": "filósofo grego, discípulo de Platão, fundador da lógica formal",
        "relacoes": ["filosofia", "logica", "platao"],
        "campo": "filosofia:antiga"
    },
    "kant": {
        "classe": "substantivo",
        "definicao": "filósofo alemão, autor da Crítica da Razão Pura",
        "relacoes": ["filosofia", "razao", "etica"],
        "campo": "filosofia:moderna"
    }
}


def adicionar_nucleo(antonia: Antonia, session_id: str, verbose: bool = True):
    """Adiciona conceitos do núcleo de conhecimento."""
    
    todos_conceitos = {**NUCLEO_CONCEITOS, **TEORIAS_CONHECIDAS, **FILOSOFOS}
    
    print("\n" + "=" * 70)
    print("FASE 1: ADICIONANDO NÚCLEO DE CONHECIMENTO")
    print("=" * 70)
    print(f"Total de conceitos: {len(todos_conceitos)}\n")
    
    for conceito, dados in todos_conceitos.items():
        cmd = f"/add {conceito} | {dados['classe']} | {dados['definicao']}"
        if dados.get('relacoes'):
            cmd += f" | {','.join(dados['relacoes'])}"
        
        resp = antonia.answer(cmd, session_id)
        
        if verbose:
            print(f"✓ {conceito:20s} [{dados['campo']}]")
    
    print(f"\n{len(todos_conceitos)} conceitos adicionados ao dicionário e grafo TRQ")
    
    # Estatísticas
    stats = antonia.graph.stats()
    print(f"Grafo TRQ: {stats['total_nodos']} nós, {stats['total_arestas']} arestas")


def criar_relacoes_fundamentais(antonia: Antonia, session_id: str):
    """Cria relações explícitas entre conceitos fundamentais."""
    
    print("\n" + "=" * 70)
    print("FASE 2: CRIANDO RELAÇÕES ESTRUTURAIS")
    print("=" * 70 + "\n")
    
    relacoes = [
        # Física
        ("energia", "trabalho", "definicao"),
        ("energia", "massa", "relacionado"),
        ("velocidade", "tempo", "parte_de"),
        ("massa", "materia", "relacionado"),
        
        # Filosofia
        ("filosofia", "epistemologia", "parte_de"),
        ("filosofia", "etica", "parte_de"),
        ("platao", "filosofia", "relacionado"),
        ("aristoteles", "platao", "relacionado"),
        
        # Teoria e ciência
        ("teoria", "hipotese", "relacionado"),
        ("relatividade", "energia", "relacionado"),
        ("relatividade", "massa", "relacionado"),
        ("evolucao", "teoria", "exemplo"),
        ("quantica", "teoria", "exemplo"),
        
        # Biologia
        ("celula", "vida", "parte_de"),
        ("dna", "gene", "parte_de"),
    ]
    
    for origem, destino, tipo in relacoes:
        cmd = f"/relacionar {origem} | {destino} | {tipo}"
        resp = antonia.answer(cmd, session_id)
        print(f"  {origem} → {destino} ({tipo})")
    
    print(f"\n{len(relacoes)} relações estruturais criadas")


def minerar_conhecimento_profundo(conceitos: list[str], verbose: bool = True):
    """
    Usa DeepSeek para minerar relações profundas.
    IMPORTANTE: Candidatos vão para QUARENTENA (validação manual).
    """
    
    print("\n" + "=" * 70)
    print("FASE 3: MINERAÇÃO COM DEEPSEEK (→ quarentena)")
    print("=" * 70 + "\n")
    
    miner = KnowledgeMiner()
    
    for conceito in conceitos:
        print(f"\n🔬 Minerando: {conceito}")
        candidatos = miner.extract_candidates(conceito, "ciencia", max_relacoes=10)
        print(f"   → {len(candidatos)} candidatos extraídos")
        
        if verbose and candidatos:
            for i, cand in enumerate(candidatos[:3], 1):
                destino = getattr(cand, "destino", getattr(cand, "alvo", getattr(cand, "target", "desconhecido")))
                print(f"      {i}. {destino} ({cand.tipo})")
                print(f"         Confiança: {cand.confianca:.2f}")
    
    print("\n⚠️  ATENÇÃO: Candidatos estão em QUARENTENA")
    print("   Para validar: /quarentena listar")
    print("   Para aprovar: /quarentena aprovar <conceito> <id>")


def bootstrap_completo(minerar: bool = False):
    """Executa bootstrap completo do conhecimento."""
    
    print("\n" + "=" * 70)
    print("🧠 BOOTSTRAP DE CONHECIMENTO DA ANTONIA")
    print("=" * 70)
    print("\nPrincípio: Conhecimento validado, estruturado e honesto\n")
    
    antonia = Antonia()
    sess = create_session("bootstrap")
    session_id = sess.session_id
    
    # Fase 1: Núcleo
    adicionar_nucleo(antonia, session_id)
    
    # Fase 2: Relações
    criar_relacoes_fundamentais(antonia, session_id)
    
    # Fase 3: Mineração (opcional - demora)
    if minerar:
        conceitos_para_minerar = [
            "energia", "massa", "velocidade",
            "filosofia", "epistemologia",
            "relatividade", "quantica"
        ]
        minerar_conhecimento_profundo(conceitos_para_minerar)
    
    # Relatório final
    print("\n" + "=" * 70)
    print("✅ BOOTSTRAP CONCLUÍDO")
    print("=" * 70)
    
    stats = antonia.graph.stats()
    print(f"\n📊 Estatísticas:")
    print(f"   • Nós no grafo: {stats['total_nodos']}")
    print(f"   • Relações: {stats['total_arestas']}")
    print(f"   • Regiões ativas: {len(stats['regioes'])}")
    
    print("\n📝 Próximos passos:")
    print("   1. Execute: python app.py")
    print("   2. Teste: 'Fale sobre a teoria da relatividade'")
    print("   3. Teste: 'Explique a filosofia de Platão'")
    print("   4. Se minerou: valide candidatos em /quarentena")
    
    print("\n💡 Lembre-se:")
    print("   • Antonia sabe APENAS o que foi ensinado/validado")
    print("   • Ela é honesta: se não sabe, diz que não sabe")
    print("   • Cada conceito novo fortalece o grafo TRQ")
    

if __name__ == "__main__":
    import sys
    
    # Permite minerar com: python bootstrap_knowledge.py --minerar
    minerar = "--minerar" in sys.argv
    
    bootstrap_completo(minerar=minerar)
