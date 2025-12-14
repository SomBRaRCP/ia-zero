# Ferramenta opcional: tenta extrair verbetes de um PDF de dicionário e mesclar em data/dictionary_pt.json.
# Heurística simples e explicável:
# - Procura linhas que parecem: "palavra <classe> <definicao>"
# - Classe aceita: m., f., adj., v. t., v. i., v. p., adv., pron., etc.
# - Definição é o resto da linha; linhas seguintes (que não começam novo verbete) são concatenadas.
#
# Se você quiser manter Python puro (sem dependências), ignore este script por enquanto.
# Se decidir usar, instale: pip install PyPDF2

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except Exception as e:
    raise SystemExit("PyPDF2 não instalado. Rode: pip install PyPDF2") from e

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

CLASS_RE = r"(m\.|f\.|adj\.|adv\.|pron\.|interj\.|prep\.|conj\.|num\.|art\.|v\.\s*t\.|v\.\s*i\.|v\.\s*p\.|pl\.)"
ENTRY_RE = re.compile(rf"^([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-']{{1,40}})\s+{CLASS_RE}\s+(.*)$")

def normalize_key(w: str) -> str:
    w = w.strip().lower()
    w = w.replace("ç","c")
    w = re.sub(r"[áàãâ]", "a", w)
    w = re.sub(r"[éèê]", "e", w)
    w = re.sub(r"[íì]", "i", w)
    w = re.sub(r"[óòõô]", "o", w)
    w = re.sub(r"[úù]", "u", w)
    w = re.sub(r"[^a-z0-9\-]", "", w)
    return w

def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    if len(sys.argv) < 2:
        print("Uso: python tools/import_dic_pdf.py caminho/para/dicionario.pdf [max_pages]")
        raise SystemExit(1)

    pdf_path = Path(sys.argv[1]).expanduser().resolve()
    max_pages = int(sys.argv[2]) if len(sys.argv) >= 3 else None

    out_path = DATA_DIR / "dictionary_pt.json"
    dic = load_json(out_path)

    reader = PdfReader(str(pdf_path))
    pages = reader.pages[:max_pages] if max_pages else reader.pages

    current = None  # (word, class, def)
    added = 0
    seen = set(dic.keys())

    def flush():
        nonlocal current, added
        if not current:
            return
        word, classe, defin = current
        key = normalize_key(word)
        if key and key not in seen and defin:
            dic[key] = {"forma": word, "classe": classe, "definicao": defin.strip(), "relacoes": []}
            seen.add(key)
            added += 1
        current = None

    for pi, page in enumerate(pages):
        text = page.extract_text() or ""
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            m = ENTRY_RE.match(line)
            if m:
                flush()
                word = m.group(1)
                classe = m.group(2)
                defin = m.group(3).strip()
                current = (word, classe, defin)
            else:
                if current and len(line) >= 3:
                    word, classe, defin = current
                    current = (word, classe, (defin + " " + line).strip())

        flush()
        if (pi + 1) % 50 == 0:
            print(f"Processadas {pi+1} páginas... adicionados={added}")

    save_json(out_path, dic)
    print(f"OK. Total no JSON: {len(dic)}. Novos adicionados: {added}. Saída: {out_path}")

if __name__ == "__main__":
    main()
