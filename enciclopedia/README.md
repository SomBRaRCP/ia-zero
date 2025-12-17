# Enciclopédia TRQ (acervo modular)

Coloque aqui arquivos `*.jsonl` (1 cartão por linha) ou `*.json` (lista/objeto com `cards`) com cartões de conhecimento.

Exemplo rápido:

```bash
python core/importar_enciclopedia_trq.py --file enciclopedia/exemplo_cards.jsonl --edges quarantine --store-resumo
```

Depois de validar os arquivos em `data/quarentena/`, colapse no grafo:

```bash
python core/colapsar_quarentena_trq.py
```

Formato detalhado: `docs/ENCICLOPEDIA_TRQ.md`

