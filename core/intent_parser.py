from dataclasses import dataclass
from core.tokenizer import normalize

@dataclass
class Intent:
    kind: str
    subject: str
    payload: str = ""

def parse_intent(user_text: str) -> Intent:
    raw = (user_text or "").strip()

    if raw.startswith("/add"):
        return Intent(kind="ensinar", subject="", payload=raw[len("/add"):].strip())

    t = normalize(user_text)

    if t.startswith("o que e ") or t.startswith("oque e "):
        return Intent(kind="definicao", subject=t.replace("o que e ", "").replace("oque e ", "").strip())

    if t.startswith("como ") or t.startswith("como fazer ") or t.startswith("como funciona "):
        subj = t.replace("como fazer ", "").replace("como funciona ", "").replace("como ", "").strip()
        return Intent(kind="como", subject=subj)

    if t.startswith("por que ") or t.startswith("porque "):
        subj = t.replace("por que ", "").replace("porque ", "").strip()
        return Intent(kind="porque", subject=subj)

    if t.startswith("liste ") or t.startswith("listar "):
        subj = t.replace("liste ", "").replace("listar ", "").strip()
        return Intent(kind="listar", subject=subj)

    return Intent(kind="desconhecida", subject=t.strip())
