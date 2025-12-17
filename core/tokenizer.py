import re

STOPWORDS = {
    "o","a","os","as","um","uma","uns","umas","de","da","do","das","dos",
    "e","é","ser","em","no","na","nos","nas","por","para","com","que",
    "qual","quais","como","porque","porquê","por","pra","onde","aonde","fica","esta","ta","isso","isto","aquele",
    "essa","esse","eu","você","vc","me","te","se","nao","não"
}

def normalize(text: str) -> str:
    t = (text or "").lower().strip()
    t = t.replace("ç","c")
    t = re.sub(r"[áàãâ]", "a", t)
    t = re.sub(r"[éèê]", "e", t)
    t = re.sub(r"[íì]", "i", t)
    t = re.sub(r"[óòõô]", "o", t)
    t = re.sub(r"[úù]", "u", t)
    t = re.sub(r"[^a-z0-9\s\-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def tokenize(text: str) -> list[str]:
    t = normalize(text)
    toks = [x for x in t.split(" ") if len(x) >= 2 and x not in STOPWORDS]
    return toks
