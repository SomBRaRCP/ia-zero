# 🎓 Como Ensinar Antonia

**Antonia agora sabe teorias científicas e conceitos filosóficos!**

---

## 📚 Conhecimento Atual (após bootstrap)

### Física
- energia, massa, velocidade
- **relatividade** (teoria de Einstein)
- **mecânica quântica**

### Filosofia
- filosofia, epistemologia, ética
- **Platão, Aristóteles, Kant**

### Biologia
- célula, DNA
- **evolução** (teoria de Darwin)

### Matemática
- número, conjunto

### Ciência
- teoria, hipótese

**Total**: 19 conceitos + 13 relações estruturais

---

## 🚀 Como Popular Mais Conhecimento

### Método 1: Bootstrap Automático (recomendado)

```bash
# Popula conhecimento fundamental
python bootstrap_knowledge.py

# Com mineração DeepSeek (demora mais, extrai relações profundas)
python bootstrap_knowledge.py --minerar
```

### Método 2: Ensino Manual via App

```bash
python app.py
```

Comandos:
```
/add conceito | classe | definição | relações_opcionais

Exemplos:
/add darwin | substantivo | naturalista inglês, autor da teoria da evolução | evolucao,selecao
/add newton | substantivo | físico inglês, autor das leis do movimento | fisica,gravidade
/add socrates | substantivo | filósofo grego, mestre de Platão | filosofia,platao
```

### Método 3: Relações Estruturais

```
/relacionar conceito1 | conceito2 | tipo

Tipos válidos:
- definicao   : X define Y
- parte_de    : X é parte de Y
- causa       : X causa Y
- relacionado : X se relaciona com Y
- exemplo     : X é exemplo de Y

Exemplos:
/relacionar newton | fisica | relacionado
/relacionar darwin | evolucao | relacionado
/relacionar socrates | platao | relacionado (Sócrates → Platão)
```

---

## 🧪 Testando Conhecimento

```bash
python test_conhecimento.py
```

Ou no app interativo:
```
python app.py

Você> Fale sobre a teoria da relatividade
Antonia> teoria (substantivo): conjunto organizado de princípios que explica fenômenos
         Conexões diretas:
         - relacionado: hipotese
         - relacionado: energia (via relatividade)

Você> Explique a filosofia de Platão
Antonia> filosofia (substantivo): estudo das questões fundamentais...
         Conexões diretas:
         - parte_de: epistemologia
         - parte_de: ética
         (Platão conectado a filosofia)
```

---

## 🔬 Mineração com DeepSeek (Avançado)

**ATENÇÃO**: Candidatos vão para QUARENTENA (validação manual obrigatória).

```bash
# No Python
from core.knowledge_miner import KnowledgeMiner

miner = KnowledgeMiner()
candidatos = miner.extract_candidates("relatividade", "fisica")
# → Candidatos vão para data/quarentena/quarentena_relatividade.json
```

No app:
```
/quarentena listar                    # Ver candidatos pendentes
/quarentena aprovar relatividade 1    # Aprovar candidato #1
```

---

## 💡 Estratégias de Expansão

### 1. **Domínios Científicos**
- Física: mecânica, termodinâmica, eletromagnetismo
- Química: átomos, moléculas, reações
- Biologia: genética, ecologia, anatomia

### 2. **História da Ciência**
- Cientistas: Einstein, Darwin, Newton, Galileu
- Descobertas: DNA, relatividade, seleção natural
- Experimentos: Michelson-Morley, Pavlov, etc.

### 3. **Filosofia Expandida**
- Escolas: estoicismo, empirismo, racionalismo
- Conceitos: verdade, justiça, liberdade
- Filósofos modernos: Descartes, Hume, Nietzsche

### 4. **Áreas Interdisciplinares**
- Lógica matemática
- Filosofia da ciência
- Ética aplicada (bioética, ética ambiental)

---

## 📊 Verificando Progresso

```bash
# No app
/graph stats

# Resultado:
Grafo TRQ:
- Nós: 19
- Relações: 13
- Regiões: geral
- Tipos usados: definicao, parte_de, relacionado, exemplo
```

---

## ⚠️ Princípios Importantes

### Antonia NÃO:
- ❌ Inventa informação que não foi ensinada
- ❌ Adiciona conhecimento automaticamente sem validação
- ❌ "Adivinha" baseado em probabilidades

### Antonia SIM:
- ✅ Sabe exatamente o que foi ensinado/validado
- ✅ Expande respostas usando grafo TRQ
- ✅ Diz "não sei" quando não tem base
- ✅ Conecta conceitos através de relações estruturais

---

## 🎯 Exemplo Completo: Ensinando Mecânica Clássica

```bash
# 1. Adiciona conceitos fundamentais
/add forca | substantivo | interação que produz aceleração em um corpo | massa,aceleracao
/add aceleracao | substantivo | taxa de variação da velocidade | velocidade,tempo
/add newton | substantivo | físico inglês, autor das leis do movimento | fisica,forca

# 2. Cria relações
/relacionar forca | aceleracao | causa
/relacionar newton | forca | relacionado
/relacionar forca | massa | relacionado

# 3. Testa
Você> Fale sobre a força
Antonia> forca (substantivo): interação que produz aceleração em um corpo
         Conexões diretas:
         - causa: aceleracao
         - relacionado: massa
         - relacionado: newton
```

---

## 🚀 Próximos Passos

1. **Execute bootstrap** (se ainda não fez):
   ```bash
   python bootstrap_knowledge.py
   ```

2. **Teste conhecimento**:
   ```bash
   python test_conhecimento.py
   ```

3. **Adicione seu domínio**: Escolha uma área (ex: astronomia, química) e popule

4. **Minere com DeepSeek** (opcional):
   ```bash
   python bootstrap_knowledge.py --minerar
   # Depois valide candidatos
   ```

5. **Compartilhe seu grafo**: O arquivo `data/trq_graph.json` pode ser compartilhado!

---

**Antonia evolui conforme você ensina. Cada conceito validado a torna mais capaz.**

**Honesta. Estruturada. Sua.**
