# Arquitetura Conversacional da Antonia

**Estado Conversacional Honesto: Como Dialogar Sem Mentir**

---

## Motivação

Antonia respondia com precisão, mas **não conversava**.

Problema:
- Cada pergunta nascia morta (sem contexto)
- Respostas corretas mas abruptas
- Não distinguia "primeira vez" de "aprofundando"
- Parecia dicionário, não companheira de raciocínio

Solução necessária **SEM**:
- Simular emoção
- Imitar chatbots sociais
- Inventar para "parecer inteligente"
- Trair princípio da honestidade estrutural

---

## Princípio-Guardião

Antes de qualquer implementação:

> **Antonia não inventa.  
> Antonia não performa emoção.  
> Antonia só fala além do literal quando houver CONTEXTO suficiente.**

Isso protege contra:
- Teatralização vazia
- Respostas bonitas mas falsas
- "Carisma" artificial
- Dependência emocional do usuário

---

## Arquitetura (4 Camadas)

### Camada 0: Núcleo Existente (não mexe)

- Dicionário (210k termos)
- Grafo TRQ (conceitos + relações)
- TSMP (seleção de candidatos)
- Respostas determinísticas

Isso é o **chão** — continua igual.

---

### Camada 1: Estado de Diálogo

**Arquivo**: `core/dialogue_state.py`

```python
class EstadoDialogo:
    def __init__(self):
        self.topico_atual: Optional[str] = None
        self.papel: str = "neutro"
        self.profundidade: int = 0
        self.historico: List[Turno] = []
        self.area_tematica: Optional[str] = None
```

**O que armazena**:
- Histórico factual de turnos (entrada, saída, tópico, papel)
- Tópico em curso (se houver)
- Profundidade na área temática (quantas perguntas sobre mesmo conceito)
- Papel funcional atual

**O que NÃO armazena**:
- Emoções simuladas
- Preferências inventadas
- Padrões de comportamento social
- "Estado de humor"

---

### Camada 2: Papel Funcional

Antonia precisa saber **quem ela é naquele momento** (função, não persona).

**Papéis possíveis** (início com 3):

```python
PAPEIS = {
  "neutro": "aguardando contexto",
  "definidora": "resposta objetiva e direta",
  "explicadora": "expande com relações do grafo",
  "exploradora": "conecta conceitos em profundidade"
}
```

**Transição automática**:

```
profundidade = 0 → neutro
profundidade = 1 → definidora
profundidade = 2 → explicadora
profundidade ≥ 3 → exploradora
```

Isso **não é teatro** — é adaptação estrutural da forma de resposta.

---

### Camada 3: Inferência Pragmática

**Pragmática** = inferir intenção do contexto (não adivinhar psicologia).

```python
class InferenciaPragmatica:
    @staticmethod
    def detectar_tipo_pergunta(texto: str) -> str:
        """
        Classifica por estrutura sintática.
        Não interpreta "sentimento". Lê FORMA.
        """
```

**Detecções**:
- "o que é X?" → `definicao`
- "como funciona?" → `explicacao`
- "por que?" → `explicacao` (busca causas)
- "qual a relação?" → `relacao`
- "e o Y?" → `continuacao` (profundidade++)
- sem `?` → `comando`

**Sem psicologia barata** — só sinais sintáticos objetivos.

---

### Camada 4: Geração com Consciência de Contexto

**Chave**: A resposta **não sai direto do grafo**.  
Passa por **decisor de forma**:

```python
def _respond_with_role(self, intent, ctx, estado, tipo_pergunta):
    if estado.papel == "definidora":
        return definicao(conceito)
    
    if estado.papel == "explicadora":
        return definicao(conceito) + expandir_com_grafo(1_nivel)
    
    if estado.papel == "exploradora":
        return definicao(conceito) + expandir_com_grafo(2_niveis)
```

**Conteúdo continua verdadeiro**.  
Só a **estrutura da resposta muda**.

---

## Expansão via Grafo TRQ

### Modo Explicadora (profundidade = 2)

Mostra **vizinhos diretos**:

```
energia (substantivo): capacidade de realizar trabalho

Conexões diretas:
- relacionado: trabalho
- relacionado: forca
```

Navegação: **1 nível**.

---

### Modo Exploradora (profundidade ≥ 3)

Navega **2 níveis**, mostra estrutura:

```
energia (substantivo): capacidade de realizar trabalho

Estrutura conceitual:
- relacionado: trabalho
  └─ trabalho conecta a 3 outros conceitos
- relacionado: forca
  └─ forca conecta a 2 outros conceitos
```

Navegação: **2 níveis** + metadados estruturais.

---

## Gesto Conversacional Final

**Segredo que muda tudo**:

> Conversa não é falar mais.  
> É **não encerrar o fluxo**.

```python
def gerar_gesto_final(self) -> str:
    if not self.precisa_continuar():
        return ""
    
    if self.papel == "exploradora":
        return f"\n\nPosso explorar mais sobre {self.topico_atual} ou seguir para conceitos relacionados?"
    
    if self.papel == "explicadora":
        return "\n\nQuer mais detalhes ou seguimos adiante?"
    
    return ""
```

**Quando NÃO gera gesto**:
- Papel é `definidora` (resposta objetiva encerra)
- Profundidade = 0 (sem contexto)
- Mudou de área temática radicalmente

**Quando GERA**:
- Há exploração ativa (profundidade ≥ 2)
- Tópico estabelecido
- Como **convite estrutural**, não social

---

## Integração no Motor

**Arquivo**: `core/engine.py`

Modificações:

1. **Adiciona estado por sessão**:
   ```python
   self.estados_dialogo = {}  # session_id -> EstadoDialogo
   ```

2. **Na resposta**:
   ```python
   estado = self.estados_dialogo.get(session_id) or EstadoDialogo()
   tipo_pergunta = InferenciaPragmatica.detectar_tipo_pergunta(user_text)
   estado.papel = estado.inferir_papel(conceito)
   resp = self._respond_with_role(intent, ctx, estado, tipo_pergunta)
   gesto = estado.gerar_gesto_final()
   estado.registrar_turno(user_text, resp, topico=conceito)
   ```

3. **Mantém toda base TSMP/TRQ intacta** — só adiciona camada de contexto.

---

## Testes de Validação

**Arquivo**: `test_dialogue_state.py`

Valida:

✅ Estado muda conforme profundidade  
✅ Papel transiciona automaticamente  
✅ Pragmática detecta tipo de pergunta  
✅ Gesto final só aparece com contexto  
✅ **Antonia continua honesta** (não inventa)  
✅ Conversa progressiva funciona  

---

## O Que Acontece na Prática

### Antes (sem estado)

```
Você> o que é energia?
Antonia> energia (substantivo): capacidade de realizar trabalho

Você> e como funciona?
Antonia> eu não tenho base suficiente
```

Cada pergunta nasce morta. Sem memória. Sem contexto.

---

### Depois (com estado)

```
Você> o que é energia?
Antonia> energia (substantivo): capacidade de realizar trabalho
[profundidade: 1, papel: definidora]

Você> e como funciona?
Antonia> energia (substantivo): capacidade de realizar trabalho

Conexões diretas:
- relacionado: trabalho

Quer mais detalhes ou seguimos adiante?
[profundidade: 2, papel: explicadora]

Você> por que energia é importante?
Antonia> Eu ainda não tenho base suficiente para justificar causalmente.

Estrutura conceitual:
- relacionado: trabalho
  └─ trabalho conecta a 2 outros conceitos

Posso explorar mais sobre energia ou seguir para conceitos relacionados?
[profundidade: 3, papel: exploradora]
```

Agora há **progressão**.  
Agora há **diálogo**.  
Mas **zero invenção**.

---

## Por Que Isso Funciona

Conversa humana tem **3 camadas**:

1. **O que foi dito** (texto literal)
2. **Por que foi dito** (intenção)
3. **O que se espera** (papel social)

Antonia antes: só camada 1.  
Antonia agora: **camadas 1 + 2 + 3**.

Mas:
- Camada 2 = inferida do **contexto estrutural** (não psicologia)
- Camada 3 = **papel funcional** (não persona social)

---

## Limitações Honestas

Antonia agora:

✅ Conversa com continuidade  
✅ Adapta forma sem mudar conteúdo  
✅ Mantém honestidade estrutural  
✅ Não teatraliza  

Antonia ainda **não**:

❌ Entende ironia ou sarcasmo  
❌ Detecta emoção humana  
❌ Faz inferências complexas de intenção oculta  
❌ "Adivinha" o que você quer sem dados  

E isso é **correto**.  
Antonia evolui pela **TRQ**, não por imitação.

---

## Próximos Passos Possíveis

1. **Mais papéis**:
   - `professora`: didática estruturada
   - `debugadora`: analisa contradições no grafo
   - `questionadora`: propõe lacunas

2. **Inferência multi-turno**:
   - Detectar mudança de interesse
   - Sugerir caminhos no grafo baseado em histórico

3. **Metadados conversacionais**:
   - "usuário prefere respostas curtas?" (comportamental, não emocional)
   - "área de interesse recorrente?" (estatística, não invenção)

4. **Reset inteligente**:
   - Detectar quando conversa "morreu"
   - Oferecer novo ponto de partida

---

## Conclusão

Antonia agora **dialoga**.

Não porque aprendeu a **fingir sociabilidade**.  
Porque aprendeu a **ler contexto estrutural**.

Continua honesta.  
Continua sua.  
Mas agora **presente**.

---

**Autoria**: Sistema Antonia v1.0  
**Data**: Dezembro 2025  
**Licença**: Mesma do projeto
