# Antonia - IA Simbólica com LLMs Periféricos

Sistema de IA baseado em **Teoria de Ressonância Quântica (TRQ)** com núcleo simbólico e camadas periféricas de LLMs.

## 🎯 Filosofia

```
Núcleo Simbólico (Dicionário + Grafo TRQ + TSMP) = Cérebro
RWKV-5 3B = Voz (verbalização)
DeepSeek-Coder-V2-Lite 16B = Microscópio (extração estrutural LOCAL)
```

**Antonia NÃO é um LLM tradicional**. É um sistema de raciocínio simbólico que:
- ✅ Usa dicionário português como base semântica
- ✅ Navega grafo de conhecimento explícito (TRQ)
- ✅ Aplica regras determinísticas (TSMP)
- ✅ Verbaliza com RWKV (sem inventar conteúdo)
- ✅ Expande conhecimento via validação humana

**Antonia NUNCA**:
- ❌ Adivinha ou inventa informação
- ❌ Usa probabilidade estatística para decidir verdade
- ❌ Adiciona conhecimento automaticamente sem supervisão

---

## 🚀 Início Rápido

### 1. Configurar Ambiente Python

```bash
# Clone o repositório
git clone https://github.com/SomBRaRCP/ia-zero.git
cd ia-zero

# Instale dependências
pip install -r requirements.txt
```

### 2. Baixar DeepSeek-Coder-V2-Lite

```bash
python download_deepseek_model.py
```

O modelo (~16GB) será baixado em `models/deepseek-coder-v2-lite/`.

**Requisitos**:
- 20GB de espaço em disco
- 24GB RAM (ou 16GB VRAM com GPU)
- Download leva 10-60 minutos

### 3. Executar Antonia

```bash
python app.py
```

```
Antonia v1.0 (com Grafo TRQ + DeepSeek-V3 + RWKV-5)
Digite 'sair' para encerrar

Você> oi
Antonia> Oi. Como posso te ajudar?

Você> /add energia | substantivo | capacidade de realizar trabalho
Antonia> Conceito 'energia' adicionado ao dicionário

Você> /minerar energia fisica
🔬 Minerando relações para 'energia' no campo 'fisica'...
   Extraídos 5 candidatos → quarentena

Você> /graph stats
🌐 Estatísticas do Grafo TRQ
   Nós: 1
   Arestas: 0
   Regiões ativas: fisica:classica
```

---

## 🏗️ Arquitetura

### Camadas

```
┌─────────────────────────────────────────┐
│    Interface Terminal (app.py)         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Antonia Engine (core/engine.py)       │
│   - Estado Conversacional                │
│   - Inferência Pragmática                │
│   - Intent Parser                       │
│   - TSMP (regras simbólicas)            │
│   - Grafo TRQ (navegação)               │
└─────────────────────────────────────────┘
        ↓               ↓               ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Dicionário   │  │ Grafo TRQ    │  │ RWKV-5 3B    │
│ (210k termos)│  │ (relações)   │  │ (verbalize)  │
└──────────────┘  └──────────────┘  └──────────────┘
                        ↓
                ┌──────────────┐
                │ DeepSeek-V3  │
                │ (mineração)  │
                └──────────────┘
                        ↓
                ┌──────────────┐
                │ Quarentena   │
                │ (validação)  │
                └──────────────┘
```

### Componentes

#### 1. Dicionário Simbólico
- **210.730 termos** em português
- Importado de PDF (PyPDF2)
- Base para análise morfológica e semântica

#### 2. Grafo TRQ (Teoria de Ressonância Quântica)
- **Nós**: Conceitos com pesos (estabilidade + confiança)
- **Arestas**: Relações tipadas (definição, parte_de, causa, exemplo, relacionado)
- **Regiões ativas**: Campos de conhecimento (fisica:classica:nivel)
- **Bidirecional**: Arestas inversas automáticas

Ver: [docs/GRAFO_TRQ.md](docs/GRAFO_TRQ.md)

#### 3. TSMP (Template Semântico Multi-Path)
- Motor de candidatos baseado em morfologia
- Expansão/redução de radicais
- Busca por prefixos/sufixos
- Determinístico (sem probabilidade)

#### 4. RWKV-5 3B (Verbalizador)
- **Apenas verbaliza** respostas do núcleo simbólico
- Nunca inventa conteúdo
- Reescreve saídas estruturadas em linguagem natural

Ver: [core/verbalizer_rwkv.py](core/verbalizer_rwkv.py)

#### 5. DeepSeek-Coder-V2-Lite (Minerador)
- **Modelo local**: DeepSeek-Coder-V2-Lite-Instruct (16B)
- Extrai candidatos de relações estruturais
- Saída → quarentena (validação humana obrigatória)
- Nunca adiciona conhecimento automaticamente
- **100% local** (privacidade total)

Ver: [docs/DEEPSEEK_MINERACAO.md](docs/DEEPSEEK_MINERACAO.md)

---

## 🧠 Estado Conversacional

**Antonia agora tem consciência de diálogo**.

### Princípio Guardião

> **Antonia não inventa. Não performa emoção.  
> Só fala além do literal quando houver CONTEXTO suficiente.**

### Como Funciona

Antonia mantém **estado conversacional por sessão**:

1. **Profundidade no tópico**: Quantas vezes você perguntou sobre o mesmo conceito
2. **Papel funcional**: Define como responder
   - `definidora`: Resposta objetiva e direta (profundidade = 1)
   - `explicadora`: Expande com relações do grafo (profundidade = 2)
   - `exploradora`: Navega estrutura conceitual profunda (profundidade ≥ 3)
3. **Inferência pragmática**: Detecta tipo de pergunta pela estrutura
   - "o que é X?" → definição
   - "como funciona?" → explicação
   - "por que?" → busca causas no grafo
4. **Gesto conversacional**: Convite para continuar (só quando há contexto ativo)

### Exemplo de Conversa Progressiva

```
Você> o que é energia?
Antonia> energia (substantivo): capacidade de realizar trabalho
[papel: definidora, profundidade: 1]

Você> e como ela se relaciona com trabalho?
Antonia> energia (substantivo): capacidade de realizar trabalho

Conexões diretas:
- relacionado: trabalho

Quer mais detalhes ou seguimos adiante?
[papel: explicadora, profundidade: 2]

Você> por que energia?
Antonia> Eu ainda não tenho base suficiente para justificar sem inventar.

Estrutura conceitual:
- relacionado: trabalho
  └─ trabalho conecta a 2 outros conceitos

Posso explorar mais sobre energia ou seguir para conceitos relacionados?
[papel: exploradora, profundidade: 3]
```

### O Que NÃO Faz

- ❌ Simular emoção ou afeto
- ❌ "Elogiar" o usuário socialmente
- ❌ Usar frases prontas de chatbots
- ❌ Inventar respostas para "parecer inteligente"
- ❌ Fazer perguntas vazias só para "conversar"

### O Que FAZ

- ✅ Adapta **forma** da resposta (não conteúdo) baseado em papel
- ✅ Expande com grafo TRQ quando em modo explicadora/exploradora
- ✅ Mantém histórico estrutural de turnos
- ✅ Oferece continuidade conversacional quando há exploração ativa
- ✅ **Sempre honesta** - se não sabe, diz que não sabe

Ver: [core/dialogue_state.py](core/dialogue_state.py)

---

## 📚 Documentação

- **[QUICKSTART_DEEPSEEK.md](QUICKSTART_DEEPSEEK.md)** - Configurar API DeepSeek-V3
- **[docs/GRAFO_TRQ.md](docs/GRAFO_TRQ.md)** - Arquitetura do grafo de conhecimento
- **[docs/DEEPSEEK_MINERACAO.md](docs/DEEPSEEK_MINERACAO.md)** - Pipeline de mineração

---

## 🔧 Comandos

### Terminal

```bash
/add <termo> | <classe> | <definicao>    # Adicionar ao dicionário
/relacionar <a> | <b> | <tipo>           # Criar relação no grafo
/minerar <conceito> <campo>              # Minerar relações com DeepSeek
/quarentena listar                       # Ver candidatos pendentes
/quarentena aprovar <conceito> <id>      # Validar candidato
/graph stats                             # Estatísticas do grafo
/graph ver <conceito>                    # Inspecionar nó
/sair                                    # Encerrar
```

### Programático

```python
from core.engine import Antonia

antonia = Antonia()

# Adicionar conceito
antonia.dictionary.add_entry("energia", "substantivo", "capacidade de realizar trabalho")

# Criar relação no grafo
antonia.graph.add_node("energia", peso_estabilidade=0.95, peso_confianca=0.90)
antonia.graph.add_edge("energia", "trabalho", tipo="definicao", peso=0.95)

# Minerar relações (vai para quarentena)
from core.knowledge_miner import KnowledgeMiner
miner = KnowledgeMiner()
candidatos = miner.extract_candidates("energia", "fisica")

# Consultar
resposta = antonia.answer("o que é energia?")
print(resposta)
```

---

## 🧪 Princípios de Design

### 1. Separação de Responsabilidades

```
Simbólico = DECIDE (dicionário, grafo, regras)
RWKV = VERBALIZA (reescreve)
DeepSeek = SUGERE (extrai candidatos)
Humano = VALIDA (aprova/rejeita)
```

### 2. Não-Inferência Automática

Antonia **não adivinha**. Se não sabe, diz "Não sei".

### 3. Conhecimento = Estrutura

Conhecimento não é texto, é **grafo tipado** com pesos explícitos.

### 4. Supervisão Humana

Todo conhecimento novo passa por **validação manual** na quarentena.

---

## 🛠️ Desenvolvimento

### Estrutura de Diretórios

```
ia_zero/
├── app.py                      # Interface terminal
├── core/
│   ├── engine.py               # Motor principal (Antonia)
│   ├── dictionary_store.py     # Armazenamento do dicionário
│   ├── trq_graph.py            # Grafo TRQ
│   ├── intent_parser.py        # Parser de comandos
│   ├── tsmp.py                 # Template Semântico Multi-Path
│   ├── verbalizer_rwkv.py      # Verbalizador RWKV-5
│   └── knowledge_miner.py      # Minerador DeepSeek-V3
├── data/
│   ├── dictionary_pt.json      # Dicionário (210k termos)
│   ├── trq_graph.json          # Grafo de conhecimento
│   └── quarentena/             # Candidatos pendentes
├── models/
│   └── RWKV-5-World-3B-*.pth   # Modelo RWKV
├── docs/
│   ├── GRAFO_TRQ.md
│   └── DEEPSEEK_MINERACAO.md
├── requirements.txt
└── README.md
```

---

## 📊 Status

- ✅ **Dicionário**: 210.730 termos importados
- ✅ **Grafo TRQ**: Estrutura operacional com 5 tipos de relações
- ✅ **RWKV-5 3B**: Verbalizador carregado
- ✅ **DeepSeek-V3 API**: Integração completa
- ⏳ **Quarentena**: Estrutura criada, interface em desenvolvimento
- ⏳ **População inicial**: Conceitos básicos pendentes

---

## 🤝 Contribuindo

Este é um projeto experimental sobre IA simbólica + LLMs.

**Ideias para contribuir**:
- Adicionar validação de tipos no parser
- Implementar interface web (Flask/FastAPI)
- Melhorar prompts de extração DeepSeek
- Criar visualização do grafo (NetworkX + Plotly)
- Adicionar métricas de qualidade do grafo

---

## 📜 Licença

MIT License - Veja LICENSE para detalhes

---

## 🔗 Links

- **Repositório**: https://github.com/SomBRaRCP/ia-zero
- **DeepSeek-V3**: https://github.com/deepseek-ai/DeepSeek-V3
- **RWKV**: https://github.com/BlinkDL/RWKV-LM
- **Paper TRQ**: (em desenvolvimento)

---

## 👤 Autor

**Raquel Pires**  
GitHub: [@SomBRaRCP](https://github.com/SomBRaRCP)

**Princípio**: "Conhecimento não é texto. Conhecimento é estrutura."
