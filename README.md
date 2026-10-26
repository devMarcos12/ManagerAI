# ManagerAI

Apoio à preparação pré-jogo de futebol com dados históricos StatsBomb Open Data.
O sistema calcula indicadores auditáveis e hipóteses condicionais, com relatórios
JSON/Markdown e interface Streamlit. A análise usa arquivos locais, sem API ou GPU.

A V3 está implementada como extensão opcional: 26 indicadores de progressão,
finalização e pressão espacial, sequências, atletas/formações históricos e dois
gráficos. Os recortes validados são Premier League 2015/16 e La Liga 2020/21.
A V3 preserva os campos legados e acrescenta `tactical_v3` no schema 1.1.0;
sem a extensão, o JSON continua no schema 1.0.0.

A V4.1 oferece contratos e adaptador do motor determinístico. A V4.3 contém
experimentos offline de previsão de finalizações e robustez temporal com OLS e
Ridge. Esses experimentos são separados das análises e hipóteses exibidas ao treinador.

## Instalação

Requer Python 3.12+. Na raiz do checkout, crie o ambiente **somente se ainda não
existir** e instale a aplicação com UI e gráficos:

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

Se o ambiente já existe, execute apenas a instalação necessária. `requirements.txt`
seleciona `.[v3]`; versões e extras `ui`, `v3`, `dev`, `experiments` e `eda` são definidos no
`pyproject.toml`. O núcleo pode ser usado sem dependências externas via
`PYTHONPATH=src`; EDA e ferramentas de desenvolvimento são opcionais. Dependências
de fine-tuning ainda não foram escolhidas. O extra `experiments` instala somente
NumPy para as regressões leves. Para instalar o núcleo sem opcionais, use
`python -m pip install .`.

O dataset é provisionado separadamente em `open-data/data/`; um clone novo do
ManagerAI não o inclui. Preserve a revisão dos dados e consulte as condições em
`open-data/README.md` e `open-data/LICENSE.pdf`. Siga o
[guia de provisionamento e licença](docs/STATSBOMB_PROVISIONING.md), que aponta ao
[contrato versionado](src/managerai/statsbomb_snapshot.json). Nunca escreva resultados nos brutos.

## Executar

```bash
MPLCONFIGDIR=/tmp/managerai-mpl venv/bin/python -B -m streamlit run streamlit_app.py
```

Abra http://localhost:8501, selecione equipes, referência e janela; confira a
cobertura e marque **Incluir análise tática por eventos (V3)** antes de analisar.
Para outra raiz de dados, configure `MANAGERAI_DATA_ROOT`.

Pela CLI, escolha um diretório de saída novo:

```bash
MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m managerai analyze --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 --target-match-id 3754314 --v3 --output-dir /tmp/managerai-city-v3-01
```

A CLI também oferece `catalog`, `teams`, `matches` e `audit`. Retire `--v3` para o
contrato legado; use a opção global `--data-root` antes do subcomando para mudar os
dados. Os resultados incluem fontes, hashes, amostras e denominadores.

Para conferir um clone StatsBomb já provisionado, sem ler integralmente os eventos:

```bash
python -B -m managerai --data-root open-data/data verify-data
```

O verificador emite JSON determinístico; código `0` indica compatibilidade com o
contrato fixado, `2` indica lacunas ou incompatibilidade. `MANAGERAI_DATA_ROOT`
também define a raiz padrão. Consulte o guia para provisionar em Linux, macOS e
PowerShell e interpretar o diagnóstico.

## Validar

```bash
PYTHONPATH=src python3 -B -S -m unittest discover -s tests -v
venv/bin/python -I -B -m unittest discover -s tests -v
MANAGERAI_RUN_LOCAL_TESTS=1 MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m unittest discover -s tests -v
PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py
```

O primeiro comando valida sem pacotes opcionais; o segundo testa o pacote instalado
sem depender de `PYTHONPATH`. O terceiro inclui dados reais, UI e gráficos quando
provisionados. Para toda a suíte portátil, instale também `.[experiments]`.
A CI de PRs e `main` testa instalação mínima e UI/V3/NumPy sem dados StatsBomb.
Os testes criam fixtures temporárias, preservam
os brutos e conferem a fixture congelada. Pulos não são testes aprovados.

## Reproduzir os experimentos

Na raiz de um checkout, com `.[experiments]` instalado e os dados StatsBomb
provisionados separadamente na revisão
`4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`, use destinos novos:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python -B -m managerai.experiments.runner --data-root open-data/data --output-dir outputs/runs/repro_ab
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 venv/bin/python -B -m managerai.experiments.robustness --data-root open-data/data --reference-artifact outputs/runs/repro_ab/run.json --output-dir outputs/runs/repro_c
```

A C aceita a referência A/B reconstruída: confere protocolo e dataset exatos e
todos os resultados por assinatura a oito casas decimais. Metadados novos de
Git/ambiente não exigem distribuir o JSON histórico. Os valores armazenados não
são arredondados por essa verificação. Os runs ficam locais e ignorados pelo Git.
Consulte os documentos operacionais abaixo para provisionamento, licenças e limitações.

- [Estado atual, arquitetura, métricas, contratos e procedimentos](docs/CURRENT_VERSION.md)
- [Pendências, decisões e resultados reais de validação](docs/PENDING.md)
- [Exemplo V3 City × Arsenal](outputs/v3_demo_city_arsenal/report.md)
- [Exemplo V3 Real × Barcelona: amostra insuficiente](outputs/v3_demo_real_madrid_barcelona/report.md)

## Limites e próximos passos

Hipóteses são regras exploratórias para revisar em vídeo/treino; não demonstram
eficácia causal. xG não é probabilidade de vitória; pressão registrada não comprova
sucesso. Amostras insuficientes geram avisos e abstenção. Contexto manual não altera
os cálculos; formações e atletas históricos não comprovam disponibilidade atual.

Modelo especializado de IA, fine-tuning, integração LLM e recomendações de
escalação **não estão implementados**. Exigem tarefa, dados/rótulos e avaliação
independentes, preservando o núcleo determinístico como baseline.
