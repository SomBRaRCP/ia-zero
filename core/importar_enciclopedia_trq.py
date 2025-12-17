#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Importador da "Enciclopedia TRQ" (cartoes) para:
- dicionario (classe + definicao curta)
- grafo TRQ (nodos + arestas tipadas)

Suporta:
- entrada JSON (lista de cards ou objeto com chave "cards")
- entrada JSONL (1 card por linha)

Modo recomendado:
- nodos entram direto (estrutura base)
- arestas vao para quarentena (validacao humana)
"""

from __future__ import annotations

# --- bootstrap path (run from different working directories) ---
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
# --------------------------------------------------------------

import argparse
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from core.dictionary_store import DictionaryStore
from core.trq_graph import TRQGraph
from core.tokenizer import normalize
from core.quarantine_store import QuarantineCandidate, upsert_candidates


TIPOS_VALIDOS = {"definicao", "parte_de", "causa", "relacionado", "exemplo"}


@dataclass(frozen=True)
class Card:
    id: str
    classe: str
    definicao_curta: str
    resumo: str
    regiao: str
    relacoes: List[Dict[str, Any]]
    exemplos: List[str]


def _load_cards(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"Arquivo nao encontrado: {path}")

    if path.suffix.lower() == ".jsonl":
        cards: List[Dict[str, Any]] = []
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                continue
            try:
                cards.append(json.loads(s))
            except json.JSONDecodeError as e:
                raise SystemExit(f"JSONL invalido em {path}:{i}: {e}")
        return cards

    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict) and isinstance(obj.get("cards"), list):
        return obj["cards"]
    raise SystemExit("Entrada JSON invalida: esperado lista ou objeto com chave 'cards'.")


def _coerce_card(raw: Dict[str, Any]) -> Optional[Card]:
    if not isinstance(raw, dict):
        return None
    cid = str(raw.get("id") or "").strip()
    if not cid:
        return None
    classe = str(raw.get("classe") or "substantivo").strip() or "substantivo"
    definicao_curta = str(raw.get("definicao_curta") or raw.get("definicao") or "").strip()
    resumo = str(raw.get("resumo") or "").strip()
    regiao = str(raw.get("regiao") or "geral:humano:1").strip() or "geral:humano:1"
    relacoes = raw.get("relacoes") or []
    if not isinstance(relacoes, list):
        relacoes = []
    exemplos = raw.get("exemplos") or []
    if isinstance(exemplos, str):
        exemplos = [exemplos]
    if not isinstance(exemplos, list):
        exemplos = []
    exemplos = [str(x) for x in exemplos if str(x).strip()]
    return Card(
        id=cid,
        classe=classe,
        definicao_curta=definicao_curta,
        resumo=resumo,
        regiao=regiao,
        relacoes=relacoes,
        exemplos=exemplos,
    )


def _load_kb(kb_path: Path) -> Dict[str, Any]:
    if kb_path.exists():
        try:
            return json.loads(kb_path.read_text(encoding="utf-8"))
        except Exception:
            return {"listas": {}, "notas": []}
    return {"listas": {}, "notas": []}


def _save_kb(kb_path: Path, kb: Dict[str, Any]) -> None:
    kb_path.write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="Arquivo JSON/JSONL de cartoes.")
    ap.add_argument(
        "--edges",
        choices=["quarantine", "direct", "skip"],
        default="quarantine",
        help="Como tratar relacoes: quarantine (default), direct (colapsa no grafo), skip (ignora).",
    )
    ap.add_argument("--force", action="store_true", help="Sobrescrever definicao no dicionario se ja existir.")
    ap.add_argument("--origin", default=None, help="Origem para nodos/arestas (default: nome do arquivo).")
    ap.add_argument("--store-resumo", action="store_true", help="Armazena 'resumo' e 'exemplos' em data/knowledge_base.json.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    in_path = Path(args.file).resolve()
    origin = args.origin or in_path.stem

    raw_cards = _load_cards(in_path)
    cards: List[Card] = []
    for rc in raw_cards:
        c = _coerce_card(rc)
        if c:
            cards.append(c)

    data_dir = _ROOT / "data"
    data_dir.mkdir(exist_ok=True)

    ds = DictionaryStore(str(data_dir / "dictionary_pt.json"))
    graph = TRQGraph(str(data_dir / "trq_graph.json"))
    quarantine_dir = data_dir / "quarentena"
    kb_path = data_dir / "knowledge_base.json"
    kb = _load_kb(kb_path) if args.store_resumo else None

    added_words = 0
    skipped_words = 0
    added_nodes = 0
    skipped_nodes = 0
    queued_edges = 0
    added_edges = 0
    skipped_edges = 0
    invalid_edges = 0

    # Para evitar duplicatas no direct (TRQGraph nao deduplica)
    existing_edge_keys = {
        (e.get("de", ""), e.get("para", ""), e.get("tipo", "")) for e in graph.data.get("arestas", [])
    }

    for card in cards:
        word_norm = normalize(card.id)

        already = ds.lookup(card.id)
        if already and not args.force:
            skipped_words += 1
        else:
            # dicionario armazena relacoes como lista de referencias simples (strings)
            rels = []
            for r in card.relacoes:
                if not isinstance(r, dict):
                    continue
                p = str(r.get("para") or "").strip()
                if p:
                    rels.append(normalize(p))
            # remove duplicatas preservando ordem
            seen = set()
            rels_dedup = []
            for r in rels:
                if r not in seen:
                    seen.add(r)
                    rels_dedup.append(r)
            ds.add(card.id, card.classe, card.definicao_curta or "", rels_dedup, save=False)
            added_words += 1

        # grafo (nodo)
        ok = graph.add_node(
            node_id=word_norm,
            definicao=card.definicao_curta or "",
            regiao=card.regiao,
            origem=origin,
            peso_estabilidade=0.9,
            peso_confianca=0.9,
            save=False,
        )
        if ok:
            added_nodes += 1
        else:
            skipped_nodes += 1

        if args.store_resumo and kb is not None:
            resumo = (card.resumo or "").strip()
            exs = [x.strip() for x in card.exemplos if x.strip()]
            parts = []
            if resumo:
                parts.append(resumo)
            if exs:
                parts.append("Exemplos: " + "; ".join(exs[:3]))
            if parts:
                note = f"[enciclopedia:{origin}] {word_norm}: " + " | ".join(parts)
                kb.setdefault("notas", [])
                if note not in kb["notas"]:
                    kb["notas"].append(note)

        # relacoes (arestas)
        if args.edges == "skip":
            continue

        quarantine_candidates: List[QuarantineCandidate] = []
        for r in card.relacoes:
            if not isinstance(r, dict):
                invalid_edges += 1
                continue
            para = str(r.get("para") or "").strip()
            tipo = str(r.get("tipo") or "").strip().lower()
            if not para or not tipo:
                invalid_edges += 1
                continue
            if tipo not in TIPOS_VALIDOS:
                invalid_edges += 1
                continue
            peso_raw = r.get("peso", r.get("confianca", 0.8))
            try:
                peso = float(peso_raw)
            except Exception:
                peso = 0.8
            peso = max(0.0, min(1.0, peso))

            de_id = str(r.get("de") or word_norm).strip()
            de_id = normalize(de_id)
            para_id = normalize(para)

            if args.edges == "quarantine":
                quarantine_candidates.append(
                    QuarantineCandidate(
                        de=de_id,
                        para=para_id,
                        tipo=tipo,
                        confianca=peso,
                        contexto=card.regiao,
                        evidencia=(card.resumo or "")[:240],
                        origem=f"enciclopedia:{origin}",
                    )
                )
                continue

            # direct
            k = (de_id, para_id, tipo)
            if k in existing_edge_keys:
                skipped_edges += 1
                continue
            if de_id not in graph.data.get("nodos", {}) or para_id not in graph.data.get("nodos", {}):
                skipped_edges += 1
                continue
            if graph.add_edge(de_id, para_id, tipo, peso=peso, origem=f"enciclopedia:{origin}", save=False):
                existing_edge_keys.add(k)
                added_edges += 1
            else:
                invalid_edges += 1

        if quarantine_candidates:
            if not args.dry_run:
                res = upsert_candidates(quarantine_dir, word_norm, quarantine_candidates)
                queued_edges += int(res.get("_added", 0))
            else:
                queued_edges += len(quarantine_candidates)

    if args.dry_run:
        print("DRY RUN")
        print(f"cards: {len(cards)}")
        print(f"dicionario: +{added_words} / {skipped_words} pulados")
        print(f"grafo nodos: +{added_nodes} / {skipped_nodes} pulados")
        if args.edges == "quarantine":
            print(f"arestas: {queued_edges} enviadas para quarentena")
        elif args.edges == "direct":
            print(f"arestas: +{added_edges} / {skipped_edges} puladas")
        print(f"arestas invalidas: {invalid_edges}")
        return 0

    ds.save()
    graph.save()
    if args.store_resumo and kb is not None:
        _save_kb(kb_path, kb)

    print("=== Importacao concluida ===")
    print(f"cards: {len(cards)}")
    print(f"dicionario: +{added_words} / {skipped_words} pulados")
    print(f"grafo nodos: +{added_nodes} / {skipped_nodes} pulados")
    if args.edges == "quarantine":
        print(f"arestas: {queued_edges} enviadas para quarentena ({quarantine_dir})")
    elif args.edges == "direct":
        print(f"arestas: +{added_edges} / {skipped_edges} puladas")
    else:
        print("arestas: ignoradas")
    print(f"arestas invalidas: {invalid_edges}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

