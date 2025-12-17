#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importador do Núcleo TI + Física para Antonia.

Uso:
  python importar_nucleo_ti_fisica.py --file nucleo_ti_fisica_v1.json
  python importar_nucleo_ti_fisica.py --file nucleo_ti_fisica_v1.json --force

O que faz:
- Insere/atualiza entradas no dictionary_pt.json
- Insere nós e relações no trq_graph.json
- Evita duplicar arestas já existentes (de, para, tipo)

Observação:
- IDs no arquivo já estão normalizados (sem acentos).
"""
from __future__ import annotations
# --- bootstrap path (auto-fix for running from different working directories) ---
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parents[1]  # project root (parent of /core)
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
# ------------------------------------------------------------------------------


import argparse
import json
from pathlib import Path
from typing import Dict, Any, Set, Tuple

def _find_project_data_dir() -> Path:
    # Tenta seguir o padrão do projeto: core/engine.py define DATA_DIR = <repo>/data
    # Aqui assumimos que este script será rodado no root do projeto (onde existe "core/").
    root = Path(__file__).resolve().parent
    # se estiver dentro de uma subpasta, sobe até achar "core"
    for _ in range(5):
        if (root / "core").exists():
            break
        root = root.parent
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Caminho do arquivo nucleo_ti_fisica_v*.json")
    ap.add_argument("--force", action="store_true", help="Sobrescrever definições já existentes no dicionário")
    args = ap.parse_args()

    nucleo_path = Path(args.file).resolve()
    if not nucleo_path.exists():
        raise SystemExit(f"Arquivo não encontrado: {nucleo_path}")

    obj: Dict[str, Any] = json.loads(nucleo_path.read_text(encoding="utf-8"))

    cards = obj.get("cards", [])
    edges = obj.get("edges", [])

    data_dir = _find_project_data_dir()

    # Importa módulos do projeto
    try:
        from core.dictionary_store import DictionaryStore
    except ModuleNotFoundError:
        # fallback when 'core' isn't resolved as a package (should be rare after sys.path bootstrap)
        from dictionary_store import DictionaryStore
    try:
        from core.trq_graph import TRQGraph
    except ModuleNotFoundError:
        from trq_graph import TRQGraph

    dict_path = data_dir / "dictionary_pt.json"
    graph_path = data_dir / "trq_graph.json"

    ds = DictionaryStore(str(dict_path))
    g = TRQGraph(str(graph_path))

    # Índice de arestas já existentes para evitar duplicação
    existing_edges: Set[Tuple[str, str, str]] = set()
    for e in g.data.get("arestas", []):
        existing_edges.add((e.get("de",""), e.get("para",""), e.get("tipo","")))

    added_words = 0
    skipped_words = 0
    added_nodes = 0
    added_edges = 0
    skipped_edges = 0

    for c in cards:
        wid = c["id"]
        word = c.get("word", wid)
        classe = c.get("classe","substantivo")
        definicao = c.get("definicao","").strip()
        regiao = c.get("regiao","geral:humano:1")
        origem = c.get("origem","nucleo")

        # Dicionário (texto + classe)
        already = ds.lookup(word)  # lookup normaliza internamente
        if already and not args.force:
            skipped_words += 1
        else:
            # "relacoes" do dicionário são apenas referências simples (strings)
            rels = []
            for r in c.get("relacoes", []):
                p = r.get("para")
                if p and p not in rels:
                    rels.append(p)
            ds.add(word, classe, definicao, rels)
            added_words += 1

        # Grafo (estrutura)
        ok = g.add_node(
            node_id=wid,
            definicao=definicao,
            regiao=regiao,
            origem=origem,
            peso_estabilidade=float(c.get("peso_estabilidade", 0.9)),
            peso_confianca=float(c.get("peso_confianca", 0.95)),
        )
        if ok:
            added_nodes += 1

    for e in edges:
        key = (e["de"], e["para"], e["tipo"])
        if key in existing_edges:
            skipped_edges += 1
            continue

        ok = g.add_edge(
            de=e["de"],
            para=e["para"],
            tipo=e["tipo"],
            peso=float(e.get("peso", 0.8)),
            origem=e.get("origem","nucleo"),
            bidirecional=False
        )
        if ok:
            existing_edges.add(key)
            added_edges += 1

    print("\n=== Importação concluída ===")
    print(f"Dicionário: {added_words} adicionadas/atualizadas, {skipped_words} puladas")
    print(f"Grafo: {added_nodes} nós novos")
    print(f"Grafo: {added_edges} arestas novas, {skipped_edges} puladas (já existiam)")
    print(f"Arquivos:")
    print(f"  - {dict_path}")
    print(f"  - {graph_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
