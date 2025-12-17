import json
from pathlib import Path
from typing import Any, Dict, Optional
from core.tokenizer import normalize

class DictionaryStore:
    # JSON com chave normalizada; 'forma' é a grafia original para exibir bonito.
    def __init__(self, path: str):
        self.path = Path(path)
        self.data: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.data = {}

    def lookup(self, word: str) -> Optional[Dict[str, Any]]:
        return self.data.get(normalize(word))

    def save(self):
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(
        self,
        word: str,
        classe: str,
        definicao: str,
        relacoes: list[str] | None = None,
        *,
        save: bool = True,
    ):
        self.data[normalize(word)] = {
            "forma": word.strip(),
            "classe": classe.strip(),
            "definicao": definicao.strip(),
            "relacoes": relacoes or []
        }
        if save:
            self.save()
