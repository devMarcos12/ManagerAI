# ManagerAI

Apoio à preparação pré-jogo de futebol com dados históricos StatsBomb Open Data.
O sistema calcula indicadores auditáveis e hipóteses condicionais, com relatórios
JSON/Markdown, interface web React e Streamlit preservado. O frontend usa a API
FastAPI local; o núcleo calcula a partir de arquivos locais, sem API externa ou GPU.

A V3 está implementada como extensão opcional: 26 indicadores de progressão,
finalização e pressão espacial, sequências, atletas/formações históricos e dois
gráficos. Os recortes validados são Premier League 2015/16 e La Liga 2020/21.
A V3 preserva os campos legados e acrescenta `tactical_v3` no schema 1.1.0;
sem a extensão, o JSON continua no schema 1.0.0.

A V4.1 oferece contratos e adaptador do motor determinístico. A V4.3 contém
experimentos offline de previsão de finalizações e robustez temporal com OLS e
Ridge. Esses experimentos são separados das análises e hipóteses exibidas ao treinador.

## Aplicação web local

Requer Python 3.12+, Node 20.19+ ou 22.12+ e os dados locais provisionados.
Use um ambiente Python novo para a web; não substitua um ambiente funcional.
Na raiz do checkout, uma vez:

```bash
python3 -m venv .venv-web
.venv-web/bin/python -m pip install '.[api,v3]'
cd frontend
# Se usar nvm: nvm install && nvm use
npm ci
cd ..
```

Com Node compatível no PATH, inicie API e interface em um único comando:

```bash
python3 -B scripts/run_web.py
```

Abra **http://127.0.0.1:5173**. A API usa `127.0.0.1:8011`, um worker; ambos
permanecem em loopback. Ctrl+C encerra somente os processos criados pelo comando.
Portas ocupadas causam erro, sem substituir servidores existentes.

O fluxo permite escolher confronto, conferir cobertura, analisar, inspecionar
indicadores/planos/evidências e exportar JSON/Markdown. V3 só é oferecida em
recortes certificados. Explicação LLM fica desativada por padrão; opcionalmente,
configure `MANAGERAI_OLLAMA_MODEL` no servidor antes de iniciar. Não há histórico
persistente: relatórios no servidor expiram; notas/relatórios não são gravados
em localStorage. Sem previsão de vitória ou escalação ideal.

Configuração pública de frontend em `frontend/.env.example`; copiar para
`frontend/.env.local` somente se necessário. Não colocar segredos em `VITE_*`.
O proxy de desenvolvimento/preview evita CORS aberto. Não há deploy ou
implantação pública nesta entrega.

```bash
cd frontend
npm run build
npm test
```

Os testes de navegador portáteis usam Playwright; para uma instalação nova,
execute `npx playwright install chromium` antes de `npm test`. Build e checks
TypeScript não precisam de navegador. Contratos, atualização de tipos e testes
reais opt-in estão em [BACKEND_API.md](docs/BACKEND_API.md).

## Instalação CLI/Streamlit

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
de treinamento foram escolhidas no extra `training` apenas para o experimento
de explicação; não são necessárias para usar a aplicação web. O extra `experiments` instala somente
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

A [matriz CORE-02](docs/season_coverage_core02.json) inventaria os 80 pares e
separa H5/H10 de calendário de calculabilidade ainda não auditada. O
[protocolo de certificação](docs/CORE02_CERTIFICATION.md) explica os gates. Nenhum
novo recorte V3 foi liberado por essa matriz.

## Validar

```bash
PYTHONPATH=src python3 -B -S -m unittest discover -s tests -v
venv/bin/python -I -B -m unittest discover -s tests -v
MANAGERAI_RUN_LOCAL_TESTS=1 MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m unittest discover -s tests -v
PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py
```

O primeiro comando valida sem pacotes opcionais; o segundo testa o pacote instalado
sem depender de `PYTHONPATH`. O terceiro inclui dados reais, UI e gráficos quando
provisionados. Para toda a suíte portátil do backend, instale também `.[experiments,api]`.
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

O serviço `2.0.0` acrescenta planos condicionais, contexto/restrições e API HTTP
opcional, preservando os schemas legados. A LLM local pode selecionar afirmações
autorizadas para uma explicação em português; o Core mantém números e decisões.
Motor tático aprendido e recomendações individuais continuam não implementados.
Fine-tuning de explicação é uma pesquisa separada com supervisão sintética,
sem validação esportiva nem promoção automática.

Para a aplicação web, consulte [contrato, execução e exemplos da API](docs/BACKEND_API.md).
Em ambiente isolado, instale `.[api,v3,experiments]` e execute:

```bash
MANAGERAI_DATA_ROOT="$PWD/open-data/data" python -I -B -m uvicorn managerai.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1
```

OpenAPI: `http://127.0.0.1:8000/openapi.json` para esse comando de API isolada.
A aplicação React abaixo usa a API em 8011 por padrão.
Resultados reais e limites de treinamento/avaliação ficam em `docs/PENDING.md`, §20.
