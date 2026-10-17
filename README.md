# ManagerAI

MVP local de apoio à preparação pré-jogo com dados históricos StatsBomb Open Data.
Produz indicadores auditáveis, hipóteses condicionais, relatório JSON e apresentação
em português. Não requer rede, API, LLM, GPU ou modelo treinado.

Recorte de demonstração: **Premier League 2015/16**, 380 partidas e 20 clubes.
O inventário também mostra outras temporadas locais, cuja adequação deve ser auditada
antes de ampliar a demonstração. Os JSONs brutos e a EDA original são preservados.

## V2.2 e V3: cobertura, padrões e visualizações

A prévia mostra o histórico disponível antes de analisar. Amostra insuficiente
recebe aviso e não gera conclusões comparativas. A extensão V3 acrescenta
26 indicadores de progressão, finalizações por zonas e pressão espacial,
sequências e participação histórica, com dois gráficos e hipóteses rastreáveis.
Formações registradas são descritivas; não há escalação sugerida ou treinamento.

```bash
MPLCONFIGDIR=/tmp/managerai-mpl venv/bin/python -m streamlit run streamlit_app.py
```

Abra **http://localhost:8501** e marque **Incluir análise tática por eventos (V3)**.
O ambiente virtual atual já tem as dependências; para um ambiente novo, instale
`requirements-v3.txt`. A CLI anterior e o JSON V1/V2 permanecem disponíveis.

- [Tutorial V3: interface, demonstração e todos os testes](docs/TUTORIAL_V3.md)
- [Entrega, validação, limitações e próximos passos](docs/RELATORIO_FINAL_V2_2_V3.md)
- [Relatório V3 City × Arsenal](outputs/v3_demo_city_arsenal/report.md)
- [Relatório V3 Real Madrid × Barcelona — amostra insuficiente](outputs/v3_demo_real_madrid_barcelona/report.md)
- [Auditoria de viabilidade dos dados](docs/V3_DATA_FEASIBILITY.md)
- [Conferência independente de métricas](docs/V3_METRICS_CHECK.md)
- [Contrato e fórmulas V3](docs/REPORT_SCHEMA_V3.md)
- [Correções da V2.2](docs/CHANGELOG_V2_2.md)

## V2: interface e relatório para a comissão técnica

A interface permite escolher equipes por nome, partida histórica ou data livre e
cenário manual; o relatório apresenta observações com números, oito indicadores
priorizados e ajustes condicionais para avaliação em treino/vídeo. Os detalhes
técnicos continuam disponíveis, e o JSON preserva o contrato da V1.

O Streamlit é opcional e fica separado do núcleo:

```bash
venv/bin/python -m pip install -r requirements-ui.txt
venv/bin/python -m streamlit run streamlit_app.py
```

Abra **http://localhost:8501**. Após iniciar o aplicativo, toda a seleção e o download
dos relatórios acontecem no navegador, sem digitar IDs ou comandos de análise.

- [Tutorial da interface e testes V2](docs/TUTORIAL_V2.md)
- [Mudanças, verificações e próximos passos](CHANGELOG_V2.md)
- [Novo relatório Manchester City × Arsenal](outputs/v2_city_arsenal/report.md)
- [JSON técnico correspondente](outputs/v2_city_arsenal/report.json)

## CLI e testes do núcleo

Requisito do núcleo V1/V2: **Python 3.12+**, apenas biblioteca padrão. A CLI `--v3` acrescenta gráficos e usa Matplotlib. O `requirements.txt`
existente pertence ao ambiente ampliado da EDA e não precisa ser instalado para o MVP.

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
PYTHONPATH=src python3 -B -m managerai teams --competition-id 2 --season-id 27
PYTHONPATH=src python3 -B -m managerai analyze --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 --target-match-id 3754314 --output-dir outputs/minha_primeira_analise
```

O último comando exige um diretório de saída **novo**. Abra `report.md` para leitura
e `report.json` para métricas, partidas-fonte, dispersão, denominadores e hashes.

- [Tutorial completo: execução, testes e diagnóstico](docs/TUTORIAL_TESTES.md)
- [Dicionário de dados e qualidade](docs/data_dictionary.md)
- [Definições das métricas e diferenças em relação à EDA](docs/metrics.md)
- [Regras das hipóteses](docs/tactical_rules.md)
- [Arquitetura e contrato do relatório](docs/architecture.md)
- [Avaliação e decisão sobre aprendizado de máquina](docs/evaluation.md)
- [Especificação do produto](SPEC_MVP_ANALISE_TATICA_STATSBOMB.md)
- [EDA original](outputs/statsbomb_eda_20261002_exec6/RELATORIO.md)

Formações, escalações, disponibilidade presente e eficácia causal não são inferidas.
Fonte dos dados: StatsBomb Open Data; consulte `open-data/README.md` e
`open-data/LICENSE.pdf`, inclusive as condições de atribuição ao compartilhar análises.
