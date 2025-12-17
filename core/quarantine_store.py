from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class QuarantineCandidate:
    de: str
    para: str
    tipo: str
    confianca: float
    contexto: str = "geral"
    evidencia: str = ""
    origem: str = "enciclopedia"


def _default_payload(conceito_raiz: str) -> Dict[str, Any]:
    return {
        "conceito_raiz": conceito_raiz,
        "timestamp": datetime.now().isoformat(),
        "total_candidatos": 0,
        "status": "aguardando_validacao",
        "candidatos": [],
    }


def quarantine_file(quarantine_dir: Path, conceito: str) -> Path:
    return quarantine_dir / f"quarentena_{conceito}.json"


def list_quarantine(quarantine_dir: Path) -> List[str]:
    if not quarantine_dir.exists():
        return []
    return sorted([p.stem.replace("quarentena_", "", 1) for p in quarantine_dir.glob("quarentena_*.json")])


def load_quarantine(quarantine_dir: Path, conceito: str) -> Optional[Dict[str, Any]]:
    qf = quarantine_file(quarantine_dir, conceito)
    if not qf.exists():
        return None
    return json.loads(qf.read_text(encoding="utf-8"))


def save_quarantine(quarantine_dir: Path, conceito: str, data: Dict[str, Any]) -> None:
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    qf = quarantine_file(quarantine_dir, conceito)
    qf.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def upsert_candidates(quarantine_dir: Path, conceito: str, candidates: List[QuarantineCandidate]) -> Dict[str, Any]:
    """
    Mescla candidatos em um arquivo de quarentena por conceito.
    Deduplica por (de, para, tipo). Mantém validação/ação existente se o candidato já existia.
    """
    data = load_quarantine(quarantine_dir, conceito) or _default_payload(conceito)
    existing: Dict[tuple[str, str, str], Dict[str, Any]] = {}
    for c in data.get("candidatos", []):
        k = (c.get("de", ""), c.get("para", ""), c.get("tipo", ""))
        existing[k] = c

    now = datetime.now().isoformat()
    added = 0
    for cand in candidates:
        k = (cand.de, cand.para, cand.tipo)
        if k in existing:
            # não sobrescreve decisão humana; mas pode atualizar metadados se ainda não validado
            if not existing[k].get("validado"):
                existing[k]["confianca"] = float(cand.confianca)
                existing[k]["contexto"] = cand.contexto
                existing[k]["evidencia"] = cand.evidencia
                existing[k]["origem"] = cand.origem
                existing[k]["timestamp"] = now
            continue

        new_entry = {
            "de": cand.de,
            "para": cand.para,
            "tipo": cand.tipo,
            "confianca": float(cand.confianca),
            "contexto": cand.contexto,
            "evidencia": cand.evidencia,
            "timestamp": now,
            "origem": cand.origem,
            "validado": False,
            "acao": None,  # aceitar|rejeitar|modificar
        }
        data.setdefault("candidatos", []).append(new_entry)
        existing[k] = new_entry
        added += 1

    total = len(data.get("candidatos", []))
    validados = sum(1 for c in data.get("candidatos", []) if c.get("validado"))
    data["total_candidatos"] = total
    data["status"] = f"validados_{validados}/{total}" if total else "aguardando_validacao"
    data["timestamp"] = now

    save_quarantine(quarantine_dir, conceito, data)
    data["_added"] = added
    return data


def export_accepted(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    accepted = []
    for c in data.get("candidatos", []):
        if c.get("validado") and c.get("acao") == "aceitar":
            accepted.append(
                {
                    "de": c["de"],
                    "para": c["para"],
                    "tipo": c["tipo"],
                    "peso": float(c.get("confianca", 0.7)),
                    "origem": str(c.get("origem", "quarentena_validada")),
                }
            )
    return accepted

