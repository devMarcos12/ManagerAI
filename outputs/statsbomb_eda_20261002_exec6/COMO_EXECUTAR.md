# Execução

No diretório do projeto, execute:

```bash
python3 scripts/run_statsbomb_eda.py
```

Dependências usadas: Python 3, pandas, pyarrow, numpy, matplotlib e seaborn (já verificadas no ambiente). O script lê somente `open-data/data`, processa eventos do recorte uma partida por vez e grava em `outputs/statsbomb_eda_20261002`; não baixa nem modifica JSONs. Em arquivos maiores que a RAM, a alternativa prevista é `ijson` para arrays JSON, que não estava instalado neste ambiente; os arquivos processados individualmente caberam na rota padrão.
