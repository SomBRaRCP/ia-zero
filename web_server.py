#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web server simples para a Antonia com seleção de modos via botões.
Executa em FastAPI e pode ser exposto via Ngrok.
"""

import re
import unicodedata
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.engine import Antonia
from core.session_store import create_session, set_profile, get_session
from core.profiles import PROFILES

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="Antonia Web", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# Sessão única compartilhada na UI web
_session = create_session(escopo_memoria="web:ngrok", profile_id="conversacional")
_session.estado_dinamico["auto_profile"] = True
_bot = Antonia()

class ChatIn(BaseModel):
    message: Optional[str] = None
    auto: Optional[bool] = None


def _strip_accents(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )


def _norm(text: str) -> str:
    return _strip_accents(text or "").lower().strip()


def _infer_profile_from_prompt(msg: str) -> str:
    """
    Heuristica simples para escolher perfil automaticamente.
    - debug: quando o usuario pede auditoria/diagnostico ou traz logs/stacktrace/codigo
    - exploratorio: quando pede mais detalhes, exemplos, passo a passo
    - trq_duro: quando pede resposta curta/definicao estrita
    - conversacional: fallback
    """
    t = _norm(msg)
    if not t:
        return "conversacional"

    # Forcar modo via prefixo (opcional):
    # ex: "modo: debug ..." / "mode: trq_duro ..." / "@exploratorio ..."
    forced = re.match(r"^(?:modo|mode)\s*[:=]\s*([a-z_]+)\b", t) or re.match(
        r"^@([a-z_]+)\b", t
    )
    if forced:
        pid = forced.group(1).strip()
        if pid in PROFILES:
            return pid
        aliases = {
            "trq": "trq_duro",
            "trq_puro": "trq_duro",
            "puro": "trq_duro",
            "exploratorio": "exploratorio",
            "conversacional": "conversacional",
            "debug": "debug",
        }
        mapped = aliases.get(pid)
        if mapped and mapped in PROFILES:
            return mapped

    debug_score = 0
    if "traceback" in t or "exception" in t or "stacktrace" in t:
        debug_score += 4
    if re.search(r"\b(erro|stack|log)\b", t):
        debug_score += 1
    if "```" in msg or ("{" in msg and "}" in msg and "\\n" in msg):
        debug_score += 2
    if re.search(r"\b(debug|auditoria|subsignals|tsmp)\b", t):
        debug_score += 4

    expl_score = 0
    if re.search(r"\b(explique|detalhe|aprofund|passo a passo|com exemplos?)\b", t):
        expl_score += 3
    if re.search(r"\b(compare|contraste|tutorial|ensine)\b", t):
        expl_score += 2
    if re.search(r"\b(como funciona|por que|porque)\b", t):
        expl_score += 1

    trq_score = 0
    if re.search(r"\b(apenas|so|somente)\b", t) and re.search(
        r"\b(definicao|defina|conceito)\b", t
    ):
        trq_score += 3
    if re.search(r"\b(curta|objetiva|resuma|resumo|em uma frase)\b", t) and re.search(
        r"\b(definicao|defina|conceito)\b", t
    ):
        trq_score += 2
    if re.search(r"\b(resposta curta|direto ao ponto|em uma frase|sem exemplos?)\b", t):
        trq_score += 3
    if re.search(r"\b(defina|definicao formal)\b", t):
        trq_score += 2

    if debug_score >= 4:
        return "debug"
    if trq_score >= 3 and trq_score >= expl_score + 1:
        return "trq_duro"
    if expl_score >= 2:
        return "exploratorio"
    return "conversacional"

@app.get("/", response_class=HTMLResponse)
async def home():
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("Arquivos web não encontrados.", status_code=500)
    return FileResponse(index_path)


@app.get("/api/state")
async def state():
    s = get_session(_session.session_id)
    if not s:
        raise HTTPException(status_code=500, detail="Sessao nao encontrada")
    return {"profile": s.profile_id, "auto": bool(s.estado_dinamico.get("auto_profile", True))}


@app.post("/api/auto/{enabled}")
async def set_auto(enabled: int):
    s = get_session(_session.session_id)
    if not s:
        raise HTTPException(status_code=500, detail="Sessao nao encontrada")
    s.estado_dinamico["auto_profile"] = bool(enabled)
    return {"ok": True, "auto": bool(s.estado_dinamico["auto_profile"]), "profile": s.profile_id}

@app.post("/api/profile/{profile_id}")
async def change_profile(profile_id: str):
    pid = profile_id.strip()
    if pid not in PROFILES:
        raise HTTPException(status_code=400, detail="Profile invalido")
    if not set_profile(_session.session_id, pid):
        raise HTTPException(status_code=500, detail="Falha ao trocar profile")
    s = get_session(_session.session_id)
    if s:
        s.estado_dinamico["auto_profile"] = False
    return {"ok": True, "profile": pid}

@app.post("/api/chat")
async def chat(body: ChatIn):
    msg = (body.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Mensagem vazia")
    s = get_session(_session.session_id)
    if not s:
        raise HTTPException(status_code=500, detail="Sessao nao encontrada")

    auto_enabled = bool(s.estado_dinamico.get("auto_profile", True))
    if body.auto is not None:
        auto_enabled = bool(body.auto)
        s.estado_dinamico["auto_profile"] = auto_enabled

    if auto_enabled:
        inferred = _infer_profile_from_prompt(msg)
        if inferred in PROFILES and inferred != s.profile_id:
            set_profile(_session.session_id, inferred)
            s = get_session(_session.session_id) or s

    reply = _bot.answer(msg, _session.session_id)
    current = s.profile_id
    return {"reply": reply, "profile": current, "auto": auto_enabled}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_server:app", host="0.0.0.0", port=8000, reload=False)
