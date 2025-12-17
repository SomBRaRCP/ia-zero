# Núcleo TI + Física v2 (densidade relacional)

O `nucleo_ti_fisica_v2` mantém **o mesmo número de cards** do v1, mas aumenta a **densidade de arestas** (2x a 4x) e cria **clusters por tema** para navegação/inferência ficar mais natural.

## Gerar v2

Geração padrão (prioriza `redes` + `seguranca`, fator 3x):

```bash
python core/gerar_nucleo_ti_fisica_v2.py
```

Prioridades prontas:

```bash
python core/gerar_nucleo_ti_fisica_v2.py --priority redes_e_seguranca --factor 3
python core/gerar_nucleo_ti_fisica_v2.py --priority sistemas_operacionais --factor 3
python core/gerar_nucleo_ti_fisica_v2.py --priority fisica_em --factor 3
```

Ou informe manualmente:

```bash
python core/gerar_nucleo_ti_fisica_v2.py --priority redes,seguranca --target-edges 1200
```

Arquivo gerado: `core/nucleo_ti_fisica_v2.json`.

## Importar para o grafo/dicionário

```bash
python core/importar_nucleo_ti_fisica_fix2.py --file core/nucleo_ti_fisica_v2.json
```

Se quiser sobrescrever entradas existentes no dicionário, use `--force`.

