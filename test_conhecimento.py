#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste: Antonia aprendeu teoria e filosofia?"""

from core.engine import Antonia
from core.session_store import create_session

antonia = Antonia()
sess = create_session("teste_conhecimento")
sid = sess.session_id

print("\n" + "=" * 70)
print("TESTANDO CONHECIMENTO DA ANTONIA")
print("=" * 70 + "\n")

perguntas = [
    "Fale sobre a teoria da relatividade",
    "Explique a filosofia de Platão",
    "O que é epistemologia?",
    "Como funciona a evolução?"
]

for pergunta in perguntas:
    print(f"\n{'─'*70}")
    print(f"Você> {pergunta}")
    print(f"{'─'*70}")
    resp = antonia.answer(pergunta, sid)
    print(f"{resp}\n")

print("=" * 70)
print("FIM DOS TESTES")
print("=" * 70)
