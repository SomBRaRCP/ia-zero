from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
from core.tokenizer import tokenize

@dataclass
class Candidate:
    source: str
    text: str
    base_weight: float
    meta: Dict[str, Any]

def _length_cost(text: str) -> float:
    return min(1.0, len(text) / 1200.0)

def score(query_tokens: set[str], cand: Candidate, metadata: Dict[str, Any]) -> float:
    tokens = set(tokenize(cand.text))
    commons = len(tokens.intersection(query_tokens))

    if commons == 0 and cand.source != "subsignals":
        return -1e9

    sim = commons / ((len(tokens) ** 0.5) + 1e-6) if tokens else 0.0
    bonus = 0.0

    st = str(metadata.get("estado", "")).lower()
    if st and st in cand.text.lower():
        bonus += 0.10

    bonus += max(0.0, min(0.25, float(metadata.get("ressonancia", 0.0)) * 0.05))
    if metadata.get("modo_trq_duro") and cand.source.startswith("episodic"):
        return -1e9

    return (sim + cand.base_weight + bonus) - (0.40 * _length_cost(cand.text))

def select_top(cands: List[Candidate], query_text: str, metadata: Dict[str, Any], top_k: int, max_chars: int) -> Tuple[str, list[tuple[float, Candidate]]]:
    q_tokens = set(tokenize(query_text))
    scored: list[tuple[float, Candidate]] = []

    for c in cands:
        s = score(q_tokens, c, metadata)
        if s > 0:
            scored.append((s, c))

    scored.sort(key=lambda x: x[0], reverse=True)

    out = []
    total = 0
    seen = set()
    used = 0

    for s, c in scored:
        if used >= top_k:
            break
        snippet = " ".join(c.text.split())
        key = snippet[:180].lower()
        if key in seen:
            continue
        seen.add(key)

        line = f"- [{c.source}] {snippet}"
        if total + len(line) + 1 > max_chars:
            continue
        out.append(line)
        total += len(line) + 1
        used += 1

    return ("\n".join(out), scored)
