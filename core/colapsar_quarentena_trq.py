#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colapsa candidatos validados da quarentena no Grafo TRQ.

Quarentena:
  data/quarentena/quarentena_<conceito>.json

Regras:
- somente candidatos com {validado: true, acao: "aceitar"} viram arestas no grafo
- deduplica por (de, para, tipo) antes de adicionar
"""

from __future__ import annotations

# --- bootstrap path ---
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
# ----------------------

import argparse
import json
from typing import Any, Dict, List, Set, Tuple

from core.trq_graph import TRQGraph
from core.quarantine_store import export_accepted, load_quarantine, list_quarantine


def _edge_key(e: Dict[str, Any]) -> Tuple[str, str, str]:
    return (str(e.get("de", "")), str(e.get("para", "")), str(e.get("tipo", "")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concept", default=None, help="Colapsar apenas um conceito (id do arquivo).")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data_dir = _ROOT / "data"
    quarantine_dir = data_dir / "quarentena"
    graph = TRQGraph(str(data_dir / "trq_graph.json"))

    conceitos = [args.concept] if args.concept else list_quarantine(quarantine_dir)
    if not conceitos:
        print("Nenhum arquivo de quarentena encontrado.")
        return 0

    existing: Set[Tuple[str, str, str]] = {
        (e.get("de", ""), e.get("para", ""), e.get("tipo", "")) for e in graph.data.get("arestas", [])
    }

    add_ok = 0
    add_skip = 0
    missing_nodes = 0

    pending_to_add: List[Dict[str, Any]] = []
    for conceito in conceitos:
        data = load_quarantine(quarantine_dir, conceito)
        if not data:
            continue
        accepted = export_accepted(data)
        for e in accepted:
            k = _edge_key(e)
            if k in existing:
                add_skip += 1
                continue
            if e["de"] not in graph.data.get("nodos", {}) or e["para"] not in graph.data.get("nodos", {}):
                missing_nodes += 1
                continue
            pending_to_add.append(e)
            existing.add(k)

    if args.dry_run:
        print("DRY RUN")
        print(f"conceitos: {len(conceitos)}")
        print(f"aceitas para adicionar: {len(pending_to_add)}")
        print(f"puladas (duplicadas): {add_skip}")
        print(f"puladas (nodo ausente): {missing_nodes}")
        return 0

    if pending_to_add:
        graph.data.setdefault("arestas", []).extend(pending_to_add)
        graph.save()
        add_ok = len(pending_to_add)

    print("=== Colapso concluido ===")
    print(f"conceitos: {len(conceitos)}")
    print(f"arestas adicionadas: {add_ok}")
    print(f"arestas puladas (duplicadas): {add_skip}")
    print(f"arestas puladas (nodo ausente): {missing_nodes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

