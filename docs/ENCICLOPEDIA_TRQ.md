# Enciclopédia TRQ (cartões de conhecimento)

A Enciclopédia TRQ é um acervo **operacional** (pequeno, verificável e modular) que alimenta a Antonia do jeito que o núcleo simbólico “engole” melhor:

- **Dicionário**: `classe + definição curta`
- **Grafo TRQ**: `conceitos + relações tipadas + pesos + região`
- **Validação humana**: relações podem entrar por **quarentena** antes de colapsar no grafo

## 1) Formato-base (cartão)

Cada cartão é um objeto JSON com o mínimo necessário para “colapsar” em dicionário + grafo.

Campos recomendados:

```json
{
  "id": "energia",
  "classe": "substantivo",
  "definicao_curta": "capacidade de realizar trabalho ou produzir mudanças",
  "resumo": "Em física, energia aparece em várias formas (cinética, potencial...) e se conserva em sistemas isolados.",
  "regiao": "fisica:classica:1",
  "relacoes": [
    {"para": "trabalho", "tipo": "definicao", "peso": 0.95},
    {"para": "movimento", "tipo": "causa", "peso": 0.80},
    {"para": "massa", "tipo": "relacionado", "peso": 0.70}
  ],
  "exemplos": ["Um corpo em queda ganha energia cinética."]
}
```

Regras:

- `id` deve ser **normalizável** (a ingestão normaliza para evitar duplicações).
- `tipo` deve ser um de: `definicao`, `parte_de`, `causa`, `relacionado`, `exemplo`.
- `peso` é `0.0–1.0` (se ausente, usa um padrão conservador).

## 2) Acervo: JSON ou JSONL

Você pode armazenar os cartões de duas formas:

- **JSON**: lista de cartões ou objeto com chave `cards`
- **JSONL**: um cartão por linha (bom para modularizar por domínio)

## 3) Ingestão (dicionário + grafo) com quarentena

Use o importador:

```bash
python core/importar_enciclopedia_trq.py --file enciclopedia/fisica_basico.jsonl --edges quarantine
```

Isso:

- adiciona/atualiza o **dicionário** (definições curtas)
- adiciona nós no **grafo TRQ**
- envia **relações** para a **quarentena** em `data/quarentena/`

Se quiser colapsar relações direto no grafo (sem quarentena):

```bash
python core/importar_enciclopedia_trq.py --file enciclopedia/fisica_basico.jsonl --edges direct
```

## 4) Colapso: quarentena -> grafo TRQ

Depois da validação humana nos arquivos `data/quarentena/quarentena_*.json`, colapse as relações aceitas:

```bash
python core/colapsar_quarentena_trq.py
```

Opções úteis:

- `--concept energia` para colapsar só um conceito
- `--dry-run` para ver o que seria aplicado

