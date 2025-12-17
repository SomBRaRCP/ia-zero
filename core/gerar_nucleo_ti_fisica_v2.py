#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de núcleo TI + Física v2 (densidade relacional).

Objetivo:
- manter o mesmo número de cards do v1 (controle);
- aumentar o número de arestas (+2x a +4x) com clusters por tema;
- permitir escolher "prioridade" de densificação (ex.: redes+segurança, SO, física EM).

Uso:
  python core/gerar_nucleo_ti_fisica_v2.py
  python core/gerar_nucleo_ti_fisica_v2.py --priority redes_e_seguranca --factor 3
  python core/gerar_nucleo_ti_fisica_v2.py --priority sistemas_operacionais --factor 3.5
  python core/gerar_nucleo_ti_fisica_v2.py --priority fisica_em --factor 3
  python core/gerar_nucleo_ti_fisica_v2.py --priority redes,seguranca --target-edges 1200
"""

from __future__ import annotations

import argparse
import json
import random
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

TIPOS_VALIDOS: Set[str] = {"definicao", "parte_de", "causa", "relacionado", "exemplo"}


_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOPWORDS = {
    "de",
    "da",
    "do",
    "das",
    "dos",
    "e",
    "em",
    "para",
    "por",
    "com",
    "sem",
    "um",
    "uma",
    "o",
    "a",
    "os",
    "as",
}


def _strip_accents(text: str) -> str:
    return "".join(
        ch
        for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )


def _normalize(text: str) -> str:
    return _strip_accents(text).lower()


def _tokenize(text: str) -> Set[str]:
    tokens = set(_TOKEN_RE.findall(_normalize(text)))
    return {t for t in tokens if t and t not in _STOPWORDS}


def _card_text(card: Dict[str, Any]) -> str:
    return " ".join(
        [
            str(card.get("id", "")),
            str(card.get("word", "")),
            str(card.get("definicao", "")),
            str(card.get("regiao", "")),
        ]
    )


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    union = len(a | b)
    return inter / union if union else 0.0


def _theme_from_regiao(regiao: str) -> str:
    r = (regiao or "").strip().lower()
    if r.startswith("ti:redes"):
        return "redes"
    if r.startswith("ti:seguranca"):
        return "seguranca"
    if r.startswith("ti:sistemas"):
        return "so"
    if r.startswith("fisica:mecanica"):
        return "mecanica"
    if r.startswith("fisica:eletromagnetismo") or r.startswith("fisica:ondas"):
        return "em"
    if r.startswith("fisica:termodinamica"):
        return "termo"
    return "outros"


HUB_PREFERENCES: Dict[str, List[str]] = {
    "redes": ["rede de computadores", "tcp ip", "ip"],
    "seguranca": ["seguranca da informacao", "criptografia", "autenticacao"],
    "so": ["sistema operacional", "kernel", "processo"],
    "mecanica": ["lei de newton", "forca", "energia", "massa"],
    "em": ["campo eletrico", "campo magnetico", "onda eletromagnetica", "maxwell"],
    "termo": ["calor", "entropia", "temperatura", "primeira lei da termodinamica"],
}


PRESET_PRIORITIES: Dict[str, List[str]] = {
    "redes_e_seguranca": ["redes", "seguranca"],
    "sistemas_operacionais": ["so"],
    "fisica_em": ["em"],
}


def _parse_priority(value: str) -> List[str]:
    v = (value or "").strip().lower()
    if not v:
        return []
    if v in PRESET_PRIORITIES:
        return PRESET_PRIORITIES[v][:]
    # aceita "redes,seguranca" ou "redes seguranca"
    v = v.replace(";", ",").replace(" ", ",")
    items = [x.strip() for x in v.split(",") if x.strip()]
    allowed = {"redes", "seguranca", "so", "mecanica", "em", "termo"}
    return [x for x in items if x in allowed]


def _choose_hub(theme: str, node_ids: Sequence[str], tokens: Dict[str, Set[str]]) -> Optional[str]:
    prefs = HUB_PREFERENCES.get(theme, [])
    node_set = set(node_ids)
    for pid in prefs:
        if pid in node_set:
            return pid
    # fallback: escolhe o nó mais "central" por similaridade média (barato o suficiente para clusters)
    best_id = None
    best_score = -1.0
    node_list = list(node_ids)
    for nid in node_list:
        t = tokens.get(nid, set())
        if not t:
            continue
        score = 0.0
        for other in node_list:
            if other == nid:
                continue
            score += _jaccard(t, tokens.get(other, set()))
        if score > best_score:
            best_score = score
            best_id = nid
    return best_id


@dataclass(frozen=True)
class EdgeKey:
    de: str
    para: str
    tipo: str


def _add_edge(
    *,
    edges: List[Dict[str, Any]],
    edge_keys: Set[EdgeKey],
    node_ids: Set[str],
    de: str,
    para: str,
    tipo: str,
    peso: float,
    origem: str,
) -> bool:
    if tipo not in TIPOS_VALIDOS:
        return False
    if not de or not para or de == para:
        return False
    if de not in node_ids or para not in node_ids:
        return False
    k = EdgeKey(de=de, para=para, tipo=tipo)
    if k in edge_keys:
        return False
    edges.append(
        {
            "de": de,
            "para": para,
            "tipo": tipo,
            "peso": float(max(0.0, min(1.0, peso))),
            "origem": origem,
        }
    )
    edge_keys.add(k)
    return True


def _generate_v2(
    *,
    obj: Dict[str, Any],
    factor: Optional[float],
    target_edges: Optional[int],
    priority: List[str],
    seed: int,
) -> Dict[str, Any]:
    rng = random.Random(seed)

    cards: List[Dict[str, Any]] = list(obj.get("cards", []))
    base_edges: List[Dict[str, Any]] = list(obj.get("edges", []))
    node_ids = {c.get("id") for c in cards if c.get("id")}

    edges: List[Dict[str, Any]] = []
    edge_keys: Set[EdgeKey] = set()
    for e in base_edges:
        de = e.get("de", "")
        para = e.get("para", "")
        tipo = e.get("tipo", "")
        peso = float(e.get("peso", 0.8))
        origem = str(e.get("origem", obj.get("meta", {}).get("name", "nucleo")))
        _add_edge(
            edges=edges,
            edge_keys=edge_keys,
            node_ids=node_ids,
            de=de,
            para=para,
            tipo=tipo,
            peso=peso,
            origem=origem,
        )

    base_count = len(edges)
    if target_edges is None:
        if factor is None:
            factor = 3.0
        if not (2.0 <= factor <= 4.0):
            raise SystemExit("--factor deve estar entre 2.0 e 4.0 (ou use --target-edges).")
        target_edges = int(round(base_count * factor))
    else:
        min_target = int(round(base_count * 2.0))
        max_target = int(round(base_count * 4.0))
        if not (min_target <= target_edges <= max_target):
            raise SystemExit(
                f"--target-edges deve ficar entre {min_target} e {max_target} (2x a 4x do v1)."
            )

    tokens = {c["id"]: _tokenize(_card_text(c)) for c in cards if c.get("id")}

    # Agrupa por tema
    by_theme: Dict[str, List[str]] = defaultdict(list)
    for c in cards:
        cid = c.get("id")
        if not cid:
            continue
        theme = _theme_from_regiao(str(c.get("regiao", "")))
        by_theme[theme].append(cid)

    # Hubs por tema
    hubs: Dict[str, str] = {}
    for theme, ids in by_theme.items():
        if theme == "outros":
            continue
        hub = _choose_hub(theme, ids, tokens)
        if hub:
            hubs[theme] = hub

    # 1) "Espinha dorsal": liga cada nó ao hub do cluster (relacionado)
    for theme, ids in by_theme.items():
        if theme == "outros":
            continue
        hub = hubs.get(theme)
        if not hub:
            continue
        for nid in ids:
            if len(edges) >= target_edges:
                break
            if nid == hub:
                continue
            w = 1.25 if theme in priority else 1.0
            _add_edge(
                edges=edges,
                edge_keys=edge_keys,
                node_ids=node_ids,
                de=nid,
                para=hub,
                tipo="relacionado",
                peso=0.70 * w,
                origem="nucleo_ti_fisica_v2:cluster",
            )

    # 2) Pontes entre clusters (especialmente redes <-> segurança, SO <-> segurança, EM <-> mecânica/termo)
    bridge_pairs = [
        ("redes", "seguranca"),
        ("so", "seguranca"),
        ("em", "mecanica"),
        ("em", "termo"),
        ("mecanica", "termo"),
    ]
    for a, b in bridge_pairs:
        if len(edges) >= target_edges:
            break
        ha = hubs.get(a)
        hb = hubs.get(b)
        if not ha or not hb or ha == hb:
            continue
        _add_edge(
            edges=edges,
            edge_keys=edge_keys,
            node_ids=node_ids,
            de=ha,
            para=hb,
            tipo="relacionado",
            peso=0.85,
            origem="nucleo_ti_fisica_v2:bridge",
        )
        _add_edge(
            edges=edges,
            edge_keys=edge_keys,
            node_ids=node_ids,
            de=hb,
            para=ha,
            tipo="relacionado",
            peso=0.85,
            origem="nucleo_ti_fisica_v2:bridge",
        )

    # 3) Densificação interna por similaridade (kNN por tema)
    # Priorizados ganham mais vizinhos.
    theme_order = [t for t in ["redes", "seguranca", "so", "em", "mecanica", "termo", "outros"] if t in by_theme]
    theme_order.sort(key=lambda t: (t not in priority, t))  # priorizados primeiro

    for theme in theme_order:
        if len(edges) >= target_edges:
            break
        ids = by_theme.get(theme, [])
        if len(ids) < 3:
            continue

        base_k = 2 if theme != "outros" else 1
        k = base_k + (2 if theme in priority else 0)
        k = max(1, min(6, k))

        # pré-computa ranking de vizinhos por nó (determinístico)
        for nid in ids:
            if len(edges) >= target_edges:
                break
            src_tokens = tokens.get(nid, set())
            scored: List[Tuple[float, float, str]] = []
            for other in ids:
                if other == nid:
                    continue
                sim = _jaccard(src_tokens, tokens.get(other, set()))
                # ruído determinístico para desempate
                tie = rng.random()
                scored.append((sim, tie, other))
            scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

            # Se tudo empatar em 0, ainda assim cria conexões (cluster) para densidade.
            for sim, _tie, other in scored[:k]:
                if len(edges) >= target_edges:
                    break
                peso = 0.62 + 0.30 * sim
                _add_edge(
                    edges=edges,
                    edge_keys=edge_keys,
                    node_ids=node_ids,
                    de=nid,
                    para=other,
                    tipo="relacionado",
                    peso=peso,
                    origem=f"nucleo_ti_fisica_v2:knn:{theme}",
                )

    # 4) Se ainda faltar, adiciona algumas arestas globais "relacionado" por similaridade geral
    if len(edges) < target_edges:
        all_ids = sorted(node_ids)
        for nid in all_ids:
            if len(edges) >= target_edges:
                break
            src_tokens = tokens.get(nid, set())
            scored: List[Tuple[float, float, str]] = []
            for other in all_ids:
                if other == nid:
                    continue
                sim = _jaccard(src_tokens, tokens.get(other, set()))
                if sim <= 0:
                    continue
                scored.append((sim, rng.random(), other))
            scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
            for sim, _tie, other in scored[:2]:
                if len(edges) >= target_edges:
                    break
                _add_edge(
                    edges=edges,
                    edge_keys=edge_keys,
                    node_ids=node_ids,
                    de=nid,
                    para=other,
                    tipo="relacionado",
                    peso=0.60 + 0.25 * sim,
                    origem="nucleo_ti_fisica_v2:global",
                )

    meta = dict(obj.get("meta", {}))
    meta.update(
        {
            "name": "nucleo_ti_fisica_v2",
            "created": meta.get("created") or "2025-12-17",
            "cards": len(cards),
            "edges": len(edges),
            "schema_version": meta.get("schema_version", "1.0"),
            "relation_types": sorted(list(TIPOS_VALIDOS)),
            "generated_from": str(meta.get("name", "nucleo_ti_fisica_v1")),
            "density_factor": round(len(edges) / max(1, base_count), 3),
            "priority": priority,
            "seed": seed,
            "note": (
                "v2 gerada automaticamente a partir do v1: mesmos cards, mais arestas e clusters temáticos "
                "(redes, segurança, SO, mecânica, EM, termo)."
            ),
        }
    )

    return {"meta": meta, "cards": cards, "edges": edges}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="in_path",
        default=str(Path("core") / "nucleo_ti_fisica_v1.json"),
        help="Arquivo de entrada (v1).",
    )
    ap.add_argument(
        "--out",
        dest="out_path",
        default=str(Path("core") / "nucleo_ti_fisica_v2.json"),
        help="Arquivo de saída (v2).",
    )
    ap.add_argument(
        "--factor",
        type=float,
        default=3.0,
        help="Fator de densidade (2.0 a 4.0). Ignorado se --target-edges for usado.",
    )
    ap.add_argument(
        "--target-edges",
        type=int,
        default=None,
        help="Número alvo de arestas (deve ficar entre 2x e 4x do v1).",
    )
    ap.add_argument(
        "--priority",
        default="redes_e_seguranca",
        help="Preset (redes_e_seguranca|sistemas_operacionais|fisica_em) ou lista (ex.: redes,seguranca).",
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)
    obj = json.loads(in_path.read_text(encoding="utf-8"))

    priority = _parse_priority(args.priority)

    v2 = _generate_v2(
        obj=obj,
        factor=None if args.target_edges is not None else args.factor,
        target_edges=args.target_edges,
        priority=priority,
        seed=args.seed,
    )

    if args.dry_run:
        print(json.dumps(v2["meta"], ensure_ascii=False, indent=2))
        return 0

    out_path.write_text(json.dumps(v2, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gerado: {out_path} ({len(v2['cards'])} cards, {len(v2['edges'])} arestas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

