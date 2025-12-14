from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import secrets
from core.profiles import PROFILES

@dataclass
class Session:
    session_id: str
    escopo_memoria: str
    profile_id: str = "conversacional"
    estado_dinamico: Dict[str, Any] = field(default_factory=dict)
    episodic_memory: list[Dict[str, str]] = field(default_factory=list)

_SESSIONS: Dict[str, Session] = {}

def create_session(escopo_memoria: str, profile_id: str = "conversacional") -> Session:
    if profile_id not in PROFILES:
        profile_id = "conversacional"
    sid = secrets.token_urlsafe(16)
    s = Session(session_id=sid, escopo_memoria=escopo_memoria, profile_id=profile_id)
    _SESSIONS[sid] = s
    return s

def get_session(session_id: str) -> Optional[Session]:
    return _SESSIONS.get(session_id)

def set_profile(session_id: str, profile_id: str) -> bool:
    s = _SESSIONS.get(session_id)
    if not s:
        return False
    if profile_id not in PROFILES:
        return False
    s.profile_id = profile_id
    return True
