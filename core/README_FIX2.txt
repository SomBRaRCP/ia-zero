Substitua os arquivos correspondentes no seu projeto (core/):
- intent_parser.py
- engine.py
- templates.py

Principais melhorias:
1) Perguntas meta (ex.: 'vc sabe conversar?') respondem corretamente.
2) Extração do subject usa tokenize (ignora stopwords como 'vc').
3) Perguntas naturais de relação (sem /relacionar) tentam o grafo.
