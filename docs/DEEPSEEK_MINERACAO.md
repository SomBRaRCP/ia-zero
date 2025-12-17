# DeepSeek-V3: Mineração Estrutural de Conhecimento

## Repositório Oficial

🔗 **GitHub**: https://github.com/deepseek-ai/DeepSeek-V3  
📚 **Paper**: https://arxiv.org/abs/2412.19437  
🌐 **API**: https://platform.deepseek.com/

## Visão Geral

DeepSeek-V3 é um modelo MoE (Mixture-of-Experts) com:
- **671B parâmetros totais** (37B ativos por token)
- **128K contexto**
- **FP8 nativo** (treinamento e inferência)
- **Desempenho SOTA** em benchmarks (superior a GPT-4o em muitas tarefas)

## Princípio Fundamental

**DeepSeek-V3 NÃO é o cérebro da Antonia.**

É um **microscópio** para extração estrutural de conhecimento.

```
DeepSeek-V3 API = microscópio
Grafo TRQ = lâmina  
Antonia (RWKV) = voz
```

## Configuração da API

### Passo 1: Obter API Key

1. Acesse: https://platform.deepseek.com/
2. Crie uma conta (se necessário)
3. Navegue até **API Keys**
4. Clique em **Create API Key**
5. Copie a chave gerada

### Passo 2: Configurar Variável de Ambiente

**Windows PowerShell**:
```powershell
$env:DEEPSEEK_API_KEY = "sk-..."

# Permanente (adiciona ao perfil do sistema)
[System.Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', 'sk-...', 'User')
```

**Linux/Mac**:
```bash
export DEEPSEEK_API_KEY="sk-..."

# Permanente (adiciona ao shell profile)
echo 'export DEEPSEEK_API_KEY="sk-..."' >> ~/.bashrc  # ou ~/.zshrc
source ~/.bashrc
```

### Passo 3: Instalar Dependências

```bash
pip install openai  # Cliente compatível com API DeepSeek
```

### Passo 4: Testar Conexão

```bash
python download_deepseek_model.py
```

Saída esperada:
```
✅ API Key encontrada!
   Key: sk-xxxxxxxx...xxxx

✅ Conexão bem-sucedida!
   Resposta: Olá! Como posso ajudar?
```

## Pipeline Completo (3 Etapas)

### 1️⃣ Etapa A — Extração de Candidatos (Offline, Batch)

DeepSeek gera **candidatos estruturais**, nunca verdades absolutas.

**Prompt exemplo**:
```
Tarefa: Análise conceitual estrutural

Conceito raiz: energia
Contexto: fisica_classica

Liste relações conceituais fundamentais em JSON:
[
  {"de": "energia", "para": "trabalho", "tipo": "definicao", "confianca": 0.95},
  ...
]

Tipos válidos: definicao, parte_de, causa, relacionado, exemplo
```

**Saída parseável**:
```json
[
  {"de": "energia", "para": "trabalho", "tipo": "definicao", "confianca": 0.95},
  {"de": "energia", "para": "movimento", "tipo": "causa", "confianca": 0.85},
  {"de": "energia", "para": "calor", "tipo": "exemplo", "confianca": 0.90}
]
```

**⚠️ IMPORTANTE**: Nada entra direto no grafo. Vai para **zona de quarentena**.

### 2️⃣ Etapa B — Validação Humana (TRQ em Modo Estável)

Arquivo de quarentena: `data/quarentena/quarentena_energia.json`

Para cada candidato, você escolhe:
- ✅ **aceitar** - Entra no grafo como está
- ❌ **rejeitar** - Descartado
- ✏️ **modificar** - Ajustar tipo, peso ou conceitos
- ⏸️ **adiar** - Deixar para depois

**Regra de ouro**:
> ❌ Nada automático por enquanto

### 3️⃣ Etapa C — Colapso no Grafo TRQ

Só após validação:

```python
# Candidato aceito
graph.add_node(
    "energia", 
    "capacidade de realizar trabalho", 
    "fisica_classica:cientifico:1",
    origem="deepseek_validado",
    peso_estabilidade=0.9,
    peso_confianca=0.85
)

graph.add_edge(
    "energia", 
    "trabalho", 
    "definicao", 
    peso=0.9, 
    origem="deepseek_validado"
)
```

**Aqui ocorre o colapso do NQC** (Núcleo Quântico de Conhecimento).

## Melhorias Implementadas no Grafo TRQ

### Peso Estruturado (não mais fixo)

**Antes**:
```json
"peso": 1.0
```

**Agora**:
```json
"peso": {
  "estabilidade": 0.9,  // Quanto o conceito é central
  "confianca": 0.8      // Confiabilidade da origem
}
```

**Interpretação TRQ**:
- `estabilidade` → Quão central é o conceito no campo
- `confianca` → Grau de certeza da fonte

### Região como Campo Ativo

**Antes**:
```json
"regiao": "fisica_classica"
```

**Agora**:
```json
"regiao": {
  "nome": "fisica_classica",
  "campo": "cientifico",
  "nivel": 1
}
```

**Benefícios**:
- ✅ Atravessar regiões semânticas
- ✅ Comparar coerência entre campos
- ✅ Evitar misturas indevidas (física × metafísica)
- ✅ Hierarquia explícita

### Arestas Bidirecionais (mas explícitas)

**Não automático. Explícito.**

```python
graph.add_edge(
    "energia", 
    "trabalho", 
    "definicao",
    bidirecional=True  # Cria também: trabalho → energia (definido_por)
)
```

**Resultado**:
- energia → trabalho (definicao)
- trabalho → energia (definido_por)

**Melhora**: Consultas em ambas as direções.

## Por que DeepSeek-V3?

DeepSeek-V3 é **excelente para este trabalho** porque:

| Característica | GPT/Claude | DeepSeek-V3 |
|----------------|------------|-------------|
| Embelezamento | Alto | Baixo ✓ |
| Filosofar | Tende a isso | Evita ✓ |
| Coerência conceitual | Boa | Excelente ✓ |
| Listas estruturáveis | Sim | Sim ✓ |
| Hierarquia semântica | Média | Alta ✓ |

**Conclusão**:
- GPT/Claude → melhores para **falar**
- DeepSeek-V3 → melhor para **estruturar** ✓

## Como Isso Dá Fluidez à Antonia

**A fluidez NÃO vem do grafo.**

Vem da **separação correta de papéis**:

```
1. Grafo TRQ → fornece CONTEÚDO-BASE
2. RWKV → fornece VOZ e RITMO
3. Nenhuma inferência solta
4. Nenhuma cadeia de pensamento
```

**Antonia não "deduz". Ela navega estrutura.**

Isso é:
- ✅ Elegante
- ✅ Seguro
- ✅ Auditável
- ✅ Escalável

## Comandos de Mineração (Futuros)

```bash
# Extrair candidatos
/minerar energia fisica_classica

# Listar quarentena
/quarentena listar

# Validar candidato
/quarentena validar energia 0 aceitar

# Exportar validados para grafo
/quarentena exportar energia
```

## Arquitetura Final

```
┌─────────────────────────────────────────┐
│          DeepSeek-V3 (Offline)          │
│         Mineração Estrutural            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│       Zona de Quarentena (JSON)         │
│     Candidatos Aguardando Validação    │
└────────────────┬────────────────────────┘
                 │
                 ▼ Validação Humana
┌─────────────────────────────────────────┐
│          Grafo TRQ (Estrutura)          │
│    Conhecimento com Coluna Vertebral   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        Antonia (RWKV + Engine)          │
│      Navegação + Verbalização           │
└─────────────────────────────────────────┘
```

## Veredito

> Este Grafo TRQ + DeepSeek-V3 é uma **fundação real**,
> não uma ideia bonita.
> Ele vai escalar, vai se manter coerente,
> e vai dar à Antonia algo que quase nenhuma IA tem:
> **conhecimento com coluna vertebral**.

---

**Status**: Arquitetura definida, pipeline implementado  
**Próximo passo**: Integração com API/modelo DeepSeek-V3  
**Data**: 14 de dezembro de 2025
