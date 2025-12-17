from dataclasses import dataclass
from core.tokenizer import normalize, tokenize

@dataclass
class Intent:
    kind: str
    subject: str
    payload: str = ""

_CONTINUATION_PREFIXES = (
    "e ",
    "mas ",
    "entao ",  # "então" vira "entao" no normalize
    "agora ",
    "ok ",
    "beleza ",
    "bom ",
    "ta ",     # "tá" vira "ta"
)

def _strip_continuation_prefix(t: str) -> str:
    t = t.strip()
    changed = True
    while changed and t:
        changed = False
        for p in _CONTINUATION_PREFIXES:
            if t.startswith(p) and len(t) > len(p):
                t = t[len(p):].strip()
                changed = True
    return t

def _strip_leading_articles(t: str) -> str:
    t = (t or "").strip()
    for art in ("o ", "a ", "os ", "as "):
        if t.startswith(art) and len(t) > len(art):
            return t[len(art):].strip()
    return t

def parse_intent(user_text: str) -> Intent:
    raw = (user_text or "").strip()

    # Remove prefixos de interface acidentais (ex: "Você>")
    if raw.lower().startswith("voce>"):
        raw = raw.split(">", 1)[1].strip()

    if raw.startswith("/add"):
        return Intent(kind="ensinar", subject="", payload=raw[len("/add"):].strip())

    if raw.startswith("/graph"):
        return Intent(kind="graph_cmd", subject="", payload=raw[len("/graph"):].strip())

    if raw.startswith("/relacionar"):
        return Intent(kind="relacionar", subject="", payload=raw[len("/relacionar"):].strip())

    t0 = normalize(raw)

    # Camada "fala social" (nao depende do dicionario)
    if t0 in {"oi", "ola", "oie", "ei", "opa", "salve", "e ai", "eai", "eae", "hello", "hi", "bom dia", "boa tarde", "boa noite"}:
        return Intent(kind="saudacao", subject="", payload=t0)
    if t0 in {"tchau", "ate", "ate mais", "ate logo", "flw", "falou"}:
        return Intent(kind="despedida", subject="", payload=t0)
    if t0 in {"valeu", "vlw", "obrigado", "obrigada", "brigado", "brigada", "muito obrigado", "muito obrigada", "grato", "grata"}:
        return Intent(kind="agradecimento", subject="", payload=t0)
    if t0 in {"ok", "okay", "certo", "beleza", "blz", "show", "fechado", "top", "entendi", "perfeito", "isso", "isso ai"}:
        return Intent(kind="confirmacao", subject=t0, payload=t0)
    if t0 in {"sim", "s", "claro", "com certeza", "pode ser", "vamos", "bora"}:
        return Intent(kind="afirmacao", subject=t0, payload=t0)
    if t0 in {"nao", "n", "negativo", "de jeito nenhum"}:
        return Intent(kind="negacao", subject=t0, payload=t0)

    t = _strip_continuation_prefix(t0)

    # Perguntas estruturais "onde fica ..." (nao e definicao)
    if t.startswith(("onde ", "aonde ")):
        toks = tokenize(t)
        subj = toks[0] if toks else ""
        return Intent(kind="localizacao", subject=subj, payload=t)

    # Perguntas estruturais "em que camada ..." (OSI/TCP-IP)
    for prefix in ("em que camada ", "em qual camada ", "qual camada "):
        if t.startswith(prefix) and len(t) > len(prefix):
            resto = t[len(prefix):].strip()
            toks = tokenize(resto)
            subj = toks[0] if toks else ""
            return Intent(kind="camada", subject=subj, payload=t)

    # Padrão "o que é X"
    if t.startswith("o que e ") or t.startswith("oque e "):
        subj = t.replace("o que e ", "").replace("oque e ", "").strip()
        subj = _strip_leading_articles(subj)
        return Intent(kind="definicao", subject=subj)

    # Padrão "qual é X" ou "qual o X"
    if t.startswith("qual e ") or t.startswith("qual o ") or t.startswith("qual a "):
        subj = t.replace("qual e ", "").replace("qual o ", "").replace("qual a ", "").strip()
        return Intent(kind="definicao", subject=subj)

    # Padrão "defina X" ou "define X"
    if t.startswith("defina ") or t.startswith("define "):
        subj = t.replace("defina ", "").replace("define ", "").strip()
        return Intent(kind="definicao", subject=subj)

    # Padrão "fale sobre X", "me fale sobre X", "fala sobre X"
    if "fale sobre " in t or "fala sobre " in t or "me fale sobre " in t:
        subj = t.replace("me fale sobre ", "").replace("fale sobre ", "").replace("fala sobre ", "").strip()
        subj = _strip_leading_articles(subj)
        return Intent(kind="explicacao", subject=subj)

    # Padrão "explica X", "explique X", "me explique X"
    if t.startswith("explica ") or t.startswith("explique ") or "me explique " in t:
        subj = t.replace("me explique ", "").replace("explique ", "").replace("explica ", "").strip()
        subj = _strip_leading_articles(subj)
        return Intent(kind="explicacao", subject=subj)

    # EXEMPLO (follow-up comum)
    if "exemplo" in t:
        if "exemplo de " in t:
            subj = t.split("exemplo de ", 1)[1].strip()
            return Intent(kind="exemplo", subject=subj)
        if t.startswith("exemplo") or " um exemplo" in t:
            return Intent(kind="exemplo", subject="")

    # Como / Por que / Listar
    if t.startswith("como ") or t.startswith("como fazer ") or t.startswith("como funciona "):
        subj = t.replace("como fazer ", "").replace("como funciona ", "").replace("como ", "").strip()
        return Intent(kind="como", subject=subj)

    if t.startswith("por que ") or t.startswith("porque "):
        subj = t.replace("por que ", "").replace("porque ", "").strip()
        return Intent(kind="porque", subject=subj)

    if t.startswith("liste ") or t.startswith("listar "):
        subj = t.replace("liste ", "").replace("listar ", "").strip()
        return Intent(kind="listar", subject=subj)

    # UMA palavra -> definição
    if t and (" " not in t) and (not t.startswith("/")):
        return Intent(kind="definicao", subject=t.strip())

    return Intent(kind="desconhecida", subject=t.strip())
