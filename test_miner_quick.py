#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste rápido do KnowledgeMiner com DeepSeek"""

from core.knowledge_miner import KnowledgeMiner

print("\n=== TESTANDO KNOWLEDGE MINER (DEEPSEEK) ===\n")

miner = KnowledgeMiner()

print("Status:", "Modelo carregado" if miner.model else "Usando modo mock")
print()

if miner.model:
    print("Extraindo candidatos para 'energia' em 'fisica'...")
    candidatos = miner.extract_candidates("energia", "fisica")
    
    print(f"\n{len(candidatos)} candidatos extraídos:\n")
    for i, cand in enumerate(candidatos[:3], 1):
        print(f"{i}. {cand.conceito_relacionado} ({cand.tipo_relacao})")
        print(f"   Confiança: {cand.score_confianca:.2f}")
        print(f"   Contexto: {cand.contexto_extracao[:100]}...")
        print()
else:
    print("⚠️  Modelo não carregado. Execute: python download_deepseek_model.py")

print("=== FIM ===")
