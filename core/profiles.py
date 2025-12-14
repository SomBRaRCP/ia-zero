from dataclasses import dataclass
from typing import Dict, Set, Any

@dataclass(frozen=True)
class ProfileTSMP:
    modo_trq_duro: bool
    top_k: int
    max_chars: int
    fontes_permitidas: Set[str]

@dataclass(frozen=True)
class ProfilePrompt:
    tom: str
    rigor: str
    especulacao: str

@dataclass(frozen=True)
class Profile:
    id: str
    descricao: str
    tsmp: ProfileTSMP
    prompt: ProfilePrompt
    estado_base: Dict[str, Any]

PROFILES: Dict[str, Profile] = {
    "trq_duro": Profile(
        id="trq_duro",
        descricao="Respostas curtas, rigorosas, quase só definições/base.",
        tsmp=ProfileTSMP(
            modo_trq_duro=True,
            top_k=4,
            max_chars=900,
            fontes_permitidas={"dictionary", "kb", "subsignals"}
        ),
        prompt=ProfilePrompt(tom="analitico", rigor="alto", especulacao="baixa"),
        estado_base={"estado": "R", "ressonancia": 0.80, "curvatura_trq": 1.20, "ajuste_trq": "rigor"},
    ),
    "exploratorio": Profile(
        id="exploratorio",
        descricao="Explica mais, dá exemplos, expande a resposta.",
        tsmp=ProfileTSMP(
            modo_trq_duro=False,
            top_k=8,
            max_chars=1600,
            fontes_permitidas={"dictionary", "kb", "episodic", "subsignals"}
        ),
        prompt=ProfilePrompt(tom="exploratorio", rigor="medio", especulacao="media"),
        estado_base={"estado": "A", "ressonancia": 0.60, "curvatura_trq": 0.80, "ajuste_trq": "explorar"},
    ),
    "conversacional": Profile(
        id="conversacional",
        descricao="Diálogo fluido, didático e curto.",
        tsmp=ProfileTSMP(
            modo_trq_duro=False,
            top_k=6,
            max_chars=1400,
            fontes_permitidas={"dictionary", "kb", "episodic", "subsignals"}
        ),
        prompt=ProfilePrompt(tom="conversacional", rigor="baixo", especulacao="media"),
        estado_base={"estado": "S", "ressonancia": 0.50, "curvatura_trq": 0.40, "ajuste_trq": "dialogo"},
    ),
    "debug": Profile(
        id="debug",
        descricao="Mostra como escolheu a resposta (auditoria).",
        tsmp=ProfileTSMP(
            modo_trq_duro=False,
            top_k=10,
            max_chars=2000,
            fontes_permitidas={"*"}
        ),
        prompt=ProfilePrompt(tom="tecnico", rigor="alto", especulacao="baixa"),
        estado_base={"estado": "N", "ressonancia": 0.20, "curvatura_trq": 0.00, "ajuste_trq": "auditoria"},
    ),
}
