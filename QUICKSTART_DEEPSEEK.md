# Guia Rápido: DeepSeek-Coder-V2-Lite + Antonia

## 🚀 Início Rápido (15-30 minutos)

### 1. Instalar Dependências

```bash
pip install transformers torch accelerate huggingface_hub safetensors
```

### 2. Baixar Modelo Local

```bash
python download_deepseek_model.py
```

O script irá:
- ✅ Baixar **DeepSeek-Coder-V2-Lite-Instruct** (~16GB)
- ✅ Salvar em `models/deepseek-coder-v2-lite/`
- ✅ Testar carregamento automático

**Requisitos**:
- 📦 ~20GB de espaço em disco
- 💾 ~24GB RAM (ou 16GB VRAM se tiver GPU)
- 🌐 Conexão estável (download ~10-60 min)

### 3. Testar Modelo

```bash
python test_deepseek_integration.py
```

---

## 🔬 Usando Mineração de Conhecimento

### Exemplo Básico

```python
from core.knowledge_miner import KnowledgeMiner

# Criar minerador (modelo será carregado na primeira extração)
miner = KnowledgeMiner()

# Extrair relações sobre "energia"
candidatos = miner.extract_candidates(
    conceito_raiz="energia",
    contexto="fisica",
    max_relacoes=5
)

# Ver resultados
print(f"Extraídos {len(candidatos)} candidatos")
for c in candidatos:
    print(f"  {c.de} --[{c.tipo}]--> {c.para} (confiança: {c.confianca})")
```

### Primeira Execução

Na primeira extração, o modelo será carregado na memória:

```
🔬 Minerando relações para 'energia' no campo 'fisica'...
   🔄 Carregando DeepSeek-Coder-V2-Lite...
   📍 Dispositivo: cuda  # ou cpu
   ✅ Modelo carregado!
   🔄 Gerando extração...
   Extraídos 5 candidatos → quarentena
```

**Nota**: Carregamento inicial leva 1-3 minutos. Extrações subsequentes são instantâneas.

---

## 💻 Hardware & Desempenho

### GPU (Recomendado)

**Com NVIDIA GPU (16GB+ VRAM)**:
- Carregamento: ~2 minutos
- Extração: ~10-20 segundos
- Precisão: Alta (BF16)

```bash
# Verificar se CUDA está disponível
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### CPU (Funciona, mas mais lento)

**Sem GPU (24GB+ RAM)**:
- Carregamento: ~5 minutos
- Extração: ~60-120 segundos
- Precisão: Alta (FP32)

**Dica**: Para CPU, considere quantização INT8 (reduz uso de RAM):

```python
# TODO: Adicionar suporte a quantização
```

---

## 📊 Comparação: Local vs API

| Aspecto | DeepSeek-Coder Local | DeepSeek-V3 API |
|---------|---------------------|-----------------|
| **Setup** | 30-60 min (download) | 5 min (API key) |
| **Hardware** | GPU 16GB+ (ideal) | Qualquer PC |
| **Custo** | Zero (após setup) | ~$0.001/request |
| **Privacidade** | 100% local | Dados vão para servidor |
| **Offline** | ✅ Funciona | ❌ Precisa internet |
| **Latência** | Baixa (local) | Média (rede) |

---

## 🧪 Uso via Terminal

### Validação Humana

Os candidatos ficam em `data/quarentena/quarentena_energia.json`:

```json
{
  "conceito_raiz": "energia",
  "status": "aguardando_validacao",
  "candidatos": [
    {
      "de": "energia",
      "para": "trabalho",
      "tipo": "definicao",
      "confianca": 0.95,
      "evidencia": "Energia é a capacidade de realizar trabalho",
      "validado": false,
      "acao": null
    }
  ]
}
```

**Para validar**:
1. Revise cada candidato
2. Defina `"acao": "aceitar"` ou `"acao": "rejeitar"`
3. Ou modifique os campos antes de aceitar
4. Execute comando `/quarentena aprovar energia` (futuro)

### Integração com Grafo TRQ

Após validação, os candidatos aprovados entram no grafo:

```python
from core.engine import Antonia

antonia = Antonia()

# Após validação manual da quarentena
antonia.graph.add_node(
    "energia",
    peso_estabilidade=0.95,
    peso_confianca=0.90,
    regiao_ativa={"nome": "fisica", "campo": "classica", "nivel": 1}
)

antonia.graph.add_edge(
    "energia", "trabalho",
    tipo="definicao",
    peso=0.95,
    evidencia="Energia é a capacidade de realizar trabalho"
)
```

---

## 📊 Uso via Terminal

```bash
python app.py
```

```
Você> /minerar energia fisica
🔬 Minerando relações para 'energia' no campo 'fisica'...
   Extraídos 5 candidatos → quarentena

Você> /quarentena listar
📋 Quarentena: energia (5 candidatos aguardando validação)
  1. energia --[definicao]--> trabalho (confiança: 0.95)
  2. energia --[causa]--> movimento (confiança: 0.85)
  ...

Você> /quarentena aprovar energia 1
✅ Relação aprovada e adicionada ao grafo TRQ

Você> /graph ver energia
🌐 Nó: energia
   Região ativa: fisica:classica:1
   Estabilidade: 0.95
   Confiança: 0.90
   Arestas:
     → trabalho [definicao] (peso: 0.95)
```

---

## 🔐 Segurança

- **Nunca** commite a API key no git
- Use variáveis de ambiente
- Adicione `.env` ao `.gitignore`
- Rotacione chaves periodicamente

---

## 💰 Custos

DeepSeek-V3 API tem preços competitivos:
- **Input**: ~$0.27 por 1M tokens
- **Output**: ~$1.10 por 1M tokens

Para mineração típica:
- 1 extração (~500 tokens) = ~$0.001 (menos de 1 centavo)
- 100 extrações = ~$0.10
- 1000 extrações = ~$1.00

**Muito mais barato** que GPT-4 ou Claude!

---

## 🐛 Troubleshooting

### Erro: "DEEPSEEK_API_KEY não encontrada"

**Solução**: Configure a variável de ambiente antes de rodar:
```powershell
$env:DEEPSEEK_API_KEY = "sk-..."
python download_deepseek_model.py
```

### Erro: "Biblioteca 'openai' não encontrada"

**Solução**: Instale o cliente:
```bash
pip install openai
```

### Erro: "Rate limit exceeded"

**Solução**: Aguarde alguns segundos e tente novamente. A API tem limites de taxa.

### Erro: "Invalid API key"

**Solução**: Verifique se copiou a chave completa do painel DeepSeek.

---

## 📚 Recursos Adicionais

- **Documentação DeepSeek**: https://platform.deepseek.com/docs
- **Paper V3**: https://arxiv.org/abs/2412.19437
- **GitHub Oficial**: https://github.com/deepseek-ai/DeepSeek-V3
- **Arquitetura TRQ**: `docs/GRAFO_TRQ.md`
- **Pipeline Mineração**: `docs/DEEPSEEK_MINERACAO.md`
