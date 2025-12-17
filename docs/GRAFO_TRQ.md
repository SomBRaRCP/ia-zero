# Grafo TRQ - Malha Explícita de Conhecimento

## Conceito Fundamental

O Grafo TRQ não é um grafo genérico. É uma estrutura operacional onde:

> **Conhecimento não é texto, é estrutura.**

- **Nó (NQC)** → Conceito estável
- **Aresta** → Relação semântica explícita
- **Peso** → Densidade informacional/estabilidade
- **Região** → Campo semântico (regionalidade quântica)

## Ontologia Mínima (v1)

Começamos com **5 tipos de relação** fundamentais:

| Tipo | Significado | Exemplo |
|------|-------------|---------|
| `definicao` | X é definido por Y | energia → trabalho |
| `parte_de` | X compõe Y | átomo → molécula |
| `causa` | X provoca Y | calor → expansão |
| `relacionado` | X tem associação com Y | música → emoção |
| `exemplo` | X é um exemplo de Y | cachorro → mamífero |

## Estrutura dos Dados

### Nó (NQC)
```json
{
  "id": "energia",
  "definicao_curta": "capacidade de realizar trabalho",
  "peso": 1.0,
  "origem": "humano",
  "regiao": "fisica_classica"
}
```

### Aresta (Relação)
```json
{
  "de": "energia",
  "para": "trabalho",
  "tipo": "definicao",
  "peso": 0.9,
  "origem": "humano"
}
```

## Comandos Disponíveis

### Adicionar Conceito
```
/add energia | substantivo | capacidade de realizar trabalho
```
Isso cria tanto uma entrada no dicionário quanto um nó no grafo.

### Criar Relação
```
/relacionar energia | trabalho | definicao
```
Conecta dois conceitos existentes com uma relação tipada.

### Ver Estatísticas
```
/graph stats
```
Mostra:
- Total de nós
- Total de relações
- Regiões existentes
- Tipos de relação usados

### Inspecionar Nó
```
/graph ver energia
```
Mostra:
- Definição
- Região
- Todas as relações (entrada e saída)

## Regras de Crescimento

**Importante**: O grafo NÃO cresce automaticamente.

✅ Nós entram por:
- `/add` (manual)
- Curadoria humana
- Extração simbólica controlada (futuro)

❌ Nunca:
- Inferência automática
- "Associação mágica"
- Expansão não supervisionada

## Princípios TRQ

1. **Campo Estável**: Toda adição é um colapso supervisionado
2. **Explicitação**: Nada entra sem tipo de relação explícito
3. **Regionalidade**: Conceitos pertencem a campos semânticos
4. **Auditabilidade**: Toda relação tem origem rastreável

## Diferencial

Você não está criando um "knowledge graph" genérico.

Você está:
> **Convertendo inteligência implícita em estrutura explícita.**

Isso é:
- ✅ Científico
- ✅ Auditável
- ✅ Cumulativo
- ✅ Compatível com TRQ
- ✅ Compatível com humanos

## Próximos Passos

1. Popular com conceitos-chave do dicionário
2. Estabelecer regiões semânticas básicas
3. Criar relações de definição fundamentais
4. Testar consultas relacionais
5. Integrar com TSMP para seleção contextual

---

**Fundado em**: 14 de dezembro de 2025  
**Arquitetura**: Simbólica + Estrutural  
**Status**: Operacional v1
