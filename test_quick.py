#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste rápido de conversa"""

import sys
from core.engine import Antonia
from core.session_store import create_session

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="backslashreplace")

antonia = Antonia()
sess = create_session("teste_rapido")
sid = sess.session_id

print("\n=== TESTE: Fale sobre o universo ===\n")

resp1 = antonia.answer("oi", sid)
print(f"Você> oi")
print(f"Antonia> {resp1}\n")

resp2 = antonia.answer("Fale sobre o universo", sid)
print(f"Você> Fale sobre o universo")
print(f"Antonia> {resp2}\n")

print("=== FIM ===")
