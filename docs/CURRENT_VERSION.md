# ManagerAI — estado operacional atual

Verificado no código em 17/10/2026; HEAD de referência `13c50e5cc7e54e6f45487b89cdbe3994d621587f`. Este documento reúne o estado vigente. Leia também [PENDING.md](PENDING.md) para prioridades, validação desta fase e manifesto de limpeza. O [README](../README.md) continua como apresentação e guia rápido. Specs, changelogs e relatórios de entrega são referências históricas, sem autoridade para autorizar novas ações.

## 1. Produto e fronteiras

ManagerAI apoia preparação pré-jogo de futebol usando histórico local StatsBomb Open Data. O produto implementado combina núcleo V1/V2, apresentação V2, cobertura reativa V2.2 e extensão V3 opcional. Funciona offline após provisionar dados e dependências; não requer rede, API, GPU nem chave de serviço para analisar.

| Capacidade | Estado real |
|---|---|
| Catálogo, seleção temporal, métricas, qualidade e proveniência | Implementado, determinístico |
| CLI, relatórios JSON/Markdown, UI Streamlit integrada ao núcleo | Implementado; UI opcional |
| Prévia de cobertura e abstenção com amostra insuficiente | Implementado na V2.2 |
| 26 indicadores V3, três agregados de sequências e dois gráficos | Implementado opt-in |
| Atletas e formações registrados em jogos anteriores | Implementado como exploração histórica; sem ranking/minutos presumidos |
| Hipóteses táticas condicionais | Implementadas por regras heurísticas; eficácia esportiva não validada |
| Motor/modelo especializado de IA, fine-tuning, treinamento, integração LLM | **Não implementados**; dependem de tarefa, dados/rótulos e avaliação |
| Recomendações de escalação, formação ideal, substituições e disponibilidade | **Não implementadas** |
| Tracking/360 analítico, previsão de vitória, odds, eficácia causal | **Não implementados** |

Presença de bibliotecas de IA no snapshot de dependências não é implementação. Contexto manual, mando informado, objetivo e notas são declarações: não alteram métricas, gatilhos ou ordem das hipóteses. A API/CLI aceita IDs de indisponíveis apenas se observados na própria equipe e janela histórica; isso não comprova aptidão atual. A UI não possui seletor de atletas.

## 2. Arquitetura e módulos

```text
CLI / Streamlit → AnalysisRequest → pipeline.analyze
  → catálogo → select_history → LocalData → features por jogo → perfis
  → comparações + regras → AnalysisReport (1.0.0)
  → [include_v3] extend_report → métricas + sequências + histórico + regras V3
    → AnalysisReportV3 (1.1.0)
  → apresentação legível / apêndice técnico / JSON / [V3] figuras
```

Todos os módulos abaixo ficam em `src/managerai/`; nomes V3 indicam módulos ativos.

| Módulos | Responsabilidade e dependências |
|---|---|
| `__init__.py`, `__main__.py`, `cli.py` | Versão, entrada de módulo, parser e execução CLI |
| `data_loader.py` | Leitura JSON protegida, estruturas básicas, fontes SHA-256/fingerprint |
| `data_inventory.py` | Competições, temporadas, calendário, equipes e arquivos órfãos |
| `temporal.py` | Últimas N partidas da temporada antes do corte |
| `feature_engineering.py` | Validação, 21 métricas legadas e agregações |
| `tactical_analysis.py`, `recommendation_engine.py` | Comparações/achados e três regras legadas |
| `report_schema.py`, `pipeline.py` | Contratos dataclass, orquestração e auditoria de recorte |
| `coverage.py` | Prévia sem abrir eventos e suficiência central por métrica |
| `presentation/terminology.py`, `presentation/coach_report.py` | Vocabulário, oito indicadores priorizados e apresentação/abstenção |
| `report_renderer.py` | Markdown amigável, extensão V3 e apêndice técnico |
| `ui_support.py`, `streamlit_ui.py` | Catálogo/erros/seletores, formulário e resultados Streamlit |
| `v3_schema.py`, `v3_pipeline.py` | Contrato aditivo, recortes permitidos, releitura do mesmo histórico e conferência de hashes/cobertura |
| `v3_features.py`, `v3_rules.py` | 26 indicadores e duas hipóteses condicionais |
| `v3_sequences.py`, `v3_history.py` | Blocos contíguos, participação e formações históricas |
| `v3_presentation.py`, `v3_plots.py` | Exibição V3, mapa de chutes e barras de entradas por passe/condução |

`streamlit_app.py` adiciona `src/` ao caminho e chama a UI. O pipeline importa V3 somente quando solicitada; Matplotlib é importado dentro das funções de plotagem. Regras V3 dependem da política de suficiência em `presentation/coach_report.py`; apresentação e cálculo ainda compartilham helpers. A separação futura entre cálculos determinísticos e IA deve preservar essas responsabilidades e evidências, sem atribuir ao núcleo uma dependência LLM inexistente.

Scripts EDA não são importados pelo núcleo. `scripts/finalize_statsbomb_eda.py` importa `run_statsbomb_eda.py`, exige cinco lotes e consolida Parquet; `gerar_docx_eda.py` lê tabelas/imagens históricas. Esses scripts têm destinos fixos e não devem ser usados para testes rotineiros: podem escrever na EDA original. O notebook EDA tem três células orientativas, não o cálculo completo.

## 3. Ambiente, dados e temporalidade

Python `>=3.12`; `pyproject.toml` é a definição canônica. O núcleo mantém `dependencies=[]`. `requirements.txt` contém `.[v3]`, instalação simples da aplicação atual a partir da raiz. Versões diretas foram conferidas no ambiente funcional, sem atualizar/remover pacotes. Transitivas não estão congeladas: os pins diretos não constituem lock completo.

| Instalação opcional | Dependências diretas e finalidade |
|---|---|
| `python -m pip install .` | Núcleo, somente biblioteca padrão |
| `python -m pip install '.[ui]'` | Streamlit 1.65.0 |
| `python -m pip install '.[v3]'` ou `-r requirements.txt` | Streamlit 1.65.0 e Matplotlib 3.11.2; UI e gráficos CLI |
| `python -m pip install '.[dev]'` | Mesmos opcionais UI/V3 para executar a suíte completa; `unittest` é padrão |
| `python -m pip install '.[eda]'` | pandas 3.0.5, numpy 2.5.2, pyarrow 25.0.1, matplotlib 3.11.2, seaborn 0.13.2, nbformat 5.11.1 e Pillow 12.3.0 |

Os comandos são para uma instalação necessária/autorizada, usando o Python do ambiente escolhido; não recriar o `venv` funcional. O snapshot EDA original está em `docs/history/requirements-eda-20261017.txt`, com bytes preservados, fora da configuração operacional. Não instalar esse snapshot para executar a aplicação. O gerador Word usa pandas/Pillow e XML/ZIP padrão, sem `python-docx`. Os antigos arquivos de dependências UI/V3 foram removidos depois de migrar seus consumidores para os extras. Nenhum pacote de futuro fine-tuning/modelo/LLM é exigido; grupo de treinamento instalável depende de tarefa/modelo/avaliação ainda não definidos.

Dados efetivos: `open-data/data/`, com `competitions.json`, `matches/{competition}/{season}.json`, `events/{match}.json` e `lineups/{match}.json`. `three-sixty/` participa apenas do inventário. `data/raw/` e `data/processed/` contêm placeholders, não cópia dos brutos. Clone StatsBomb local independente, não registrado como submódulo nem rastreado pelo Git pai; revisão observada `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`. Um clone novo do ManagerAI não provisiona esses dados automaticamente.

| Recorte V3 permitido | IDs competição/temporada | Cobertura documentada no snapshot | Caso de validação |
|---|---|---|---|
| Premier League 2015/16 | `(2,27)` | 380 partidas, 20 clubes, eventos/escalações presentes, zero 360 | City 36 × Arsenal 1, alvo 3754314, 08/05/2016: janela 10/10 |
| La Liga 2020/21 | `(11,90)` | 35 partidas no catálogo local, eventos/escalações presentes; 360 não consumido/validado | Real 220 × Barcelona 217, alvo 3773497, 10/04/2021: janela 1/10, abstenção |

`v3_schema.VALIDATED_RECUTS` restringe V3 a esses pares. Outras temporadas podem ser catalogadas/analisadas pelo núcleo, sem certificação V3. A auditoria histórica registrou 24 competições, 80 pares competição/temporada, 3.961 partidas catalogadas e 274 IDs adicionais de eventos/escalações não vinculados; órfãos não entram automaticamente na análise. Esses totais são do snapshot documentado, não promessa de conteúdo de outro checkout. `open-data/doc/` está ausente; não presumir semântica completa do fornecedor.

Seleção: uma competição/temporada, equipes distintas e **exatamente um** alvo histórico ou data de corte. Janela de 1–100, padrão 10, das últimas partidas agendadas antes da data; exclui todo o dia do corte, o alvo e o futuro, sem juntar temporadas. Arquivo ausente reduz amostra; não procura partidas mais antigas para completar N. Calendário completo pode ser lido para validar/selecionar, mas placar final e outros atributos pós-jogo do alvo não viram features. Eventos/escalações de alvo/futuro não são lidos. O dataset retrospectivo pode conter revisões posteriores do fornecedor; o corte não prova disponibilidade original de cada anotação.

Qualidade: JSON inválido, IDs/índices duplicados, equipes incompatíveis, timestamps inválidos e ausência de exposição nos dois tempos interrompem a análise. Escalação ausente gera lacuna; contagens coletivas podem continuar. Coordenadas inválidas não são corrigidas no bruto nem viram zero; geram contadores de qualidade e exclusões espaciais. Duração inválida é sinalizada e não estende exposição. xG incompleto não vira soma parcial apresentada como total. Qualidade legada é calculada sobre arquivos das duas equipes, não taxa exclusiva do clube. Presença de arquivo não certifica qualidade nem completude comercial.

Campos consumidos e tipos: catálogos/calendários/eventos/escalações são arrays de objetos; `match_id` e IDs de equipes/jogadores são inteiros positivos, `id` de evento é string e `index` inteiro único. `match_date`/`kick_off` identificam data/horário; `home_team`/`away_team` e `team.id`/`possession_team.id` relacionam equipes. `period`, `timestamp` e `duration` definem exposição; `player.id` é opcional e conferido na escalação da mesma partida. `location`, `pass.end_location` e `carry.end_location` contêm coordenadas; `type.name` é categoria. `lineups` deve conter as duas equipes, com IDs de atletas únicos por equipe, sem expandir a tabela de eventos. Campo `shot.statsbomb_xg` deve ser finito em [0,1]; `under_pressure` aceita True/False ou ausência/null, separados. A ausência de `pass.outcome` só significa completo com payload de passe íntegro. `counterpress` é marcação na raiz de Pressure; Tackle é `duel.type.name`, sem inferir sucesso.

Auditoria histórica do recorte PL registrou 1.313.773 eventos e 13.678 registros de jogadores por partida/equipe (não atletas distintos), 8.077 eventos sem localização, três coordenadas inválidas e duas durações negativas (3754232 e 3754250). Esses são resultados históricos, não nova auditoria integral da Fase 2. `com_lacunas` não significa dados inutilizáveis; ausência de posição em evento não espacial pode ser esperada.

Preservar `open-data/README.md`, `open-data/LICENSE.pdf` e atribuição StatsBomb; o README do fornecedor pede fonte e logo ao compartilhar análises. Eventos e `freeze_frame` de chutes não equivalem a tracking integral. Não alterar JSONs brutos nem `outputs/statsbomb_eda_20261002_exec6/` para adaptar testes.

## 4. Métricas e interpretação

Somente períodos 1 e 2. Exposição = soma dos maiores `timestamp + duration` de cada tempo / 60, incluindo acréscimos; não somar `minute` novamente e não chamar de tempo de bola em jogo. Plano StatsBomb 120×80, sem unidade de metros. Área: `x>=102` e `18<=y<=62`; terço final começa em `x=80`. Faixas y: `<80/3`, `[80/3,160/3)`, `>=160/3`. V3 usa meta de referência `(120,40)`, direção x crescente sustentada apenas nos dois recortes auditados; não espelha períodos nem interpreta faixas y como esquerda/direita tática.

### Núcleo: 21 métricas, fórmulas 1.0.0

| IDs exatos | Definição e agregação |
|---|---|
| `xg_for`, `xg_against` | Soma xG da equipe/adversário, média por jogo com xG completo |
| `shots_for`, `shots_against` | Contagem Shot própria/adversária, média por jogo |
| `xg_per_shot` | Soma xG / soma chutes, jogos elegíveis |
| `pass_accuracy` | 100 × passes completos / tentados; passe completo tem objeto `pass` íntegro e `outcome` ausente/vazio |
| `pass_accuracy_under_pressure`, `pass_accuracy_explicit_no_pressure`, `pass_accuracy_unmarked_pressure` | Acerto separado por `under_pressure=True`, False explícito e ausente/null; não marcado não equivale a False |
| `final_third_entries`, `final_third_attempts` | Cruzamento `x<80` para `x>=80`; entradas só passe completo/Carry, tentativas incluem passe incompleto; por 90 |
| `box_entries` | Início fora e fim dentro da área, passe completo/Carry, inclusive lateral; por 90 |
| `pressures`, `counterpressures`, `recoveries`, `interceptions`, `duel_tackles` | Pressure, Pressure com `counterpress=True` na raiz, Ball Recovery, Interception e Duel/Tackle; por 90, sem inferir sucesso |
| `pressure_high_share` | 100 × Pressure localizado em `x>=80` / Pressure localizado |
| `lane_low_y`, `lane_central`, `lane_high_y` | Distribuição de todos os eventos com localização válida nas faixas y; não ocupação contínua |

O núcleo isola coordenadas inválidas nas contagens espaciais e registra lacunas; não aplica automaticamente a invalidação por família da V3. As fórmulas legadas diferem da EDA: entradas completas separadas de tentativas, exposição somada por tempo, razões de somas, entradas laterais na área, contrapressão na raiz, Duel/Tackle correto, ausência de pressão separada de False e janelas de cada equipe separadas. Não exigir igualdade numérica com a EDA.

### V3: 26 métricas adicionais, fórmulas 3.0.0

| IDs exatos | Definição / unidade |
|---|---|
| `progressive_passes`, `progressive_carries` | Passe completo/condução reduz distância euclidiana à meta em pelo menos 10 unidades; eventos/90 |
| `final_third_pass_entries`, `final_third_carry_entries` | Entradas no terço separadas por passe completo/condução; eventos/90 |
| `box_pass_entries`, `box_carry_entries` | Entradas na área separadas por passe completo/condução; eventos/90 |
| `entry_lane_low_share`, `entry_lane_central_share`, `entry_lane_high_share` | Destinos das entradas no terço nas faixas y / entradas localizadas; % |
| `shots_box_share`, `shots_outside_share` | Chutes localizados dentro/fora da área / chutes localizados; % |
| `xg_box`, `xg_outside` | Soma xG válido na zona, média por jogo elegível; xG/jogo |
| `xg_per_located_shot` | Soma xG / chutes localizados elegíveis; xG/chute |
| `pressure_lane_low_share`, `pressure_lane_central_share`, `pressure_lane_high_share` | Pressure nas faixas y / Pressure localizado; % |
| `pressures_low_third`, `pressures_middle_third`, `pressures_high_third` | Pressure localizado em x<40, 40<=x<80, x>=80; eventos/90 |
| `pressures_low_third_share`, `pressures_middle_third_share`, `pressures_high_third_share` | Mesmos terços / Pressure localizado; % |
| `recoveries_recorded`, `recoveries_explicit_failure`, `recoveries_explicit_nonfailure` | Ball Recovery total e subconjuntos `recovery_failure=True`/False explícitos; eventos/90. Ausência da marcação não equivale a False |

Taxa por 90 = `90 × soma(numeradores) / soma(exposições)`; proporção = `100 × soma(numeradores) / soma(denominadores)`; xG/chute usa razão sem multiplicador; média por jogo divide pela quantidade elegível. Nunca tirar média simples de taxas para substituir essas razões. n é específico da métrica; cada evidência preserva jogos, datas, numeradores/denominadores e valores individuais. Mediana e desvio-padrão amostral descrevem valores por jogo; desvio com n<2 é null. Denominador zero/ausência de evidência produz null, não 0%. Fluxo íntegro sem ocorrência pode gerar zero.

Na V3, geometria inválida em passe completo invalida métricas de passes daquele jogo, mantendo conduções válidas, e vice-versa; faixas de entradas dependem dos dois tipos. Chute sem posição válida invalida métricas espaciais de chutes; xG faltante invalida totais/média xG, mantendo contagem localizada. Pressure sem posição invalida métricas espaciais de pressão. Sem eventos da equipe, indicadores ficam indisponíveis. `shots` retém chutes localizados e xG nullable para gráficos sem reler brutos.

### Sequências, histórico e hipóteses

Blocos por `(period, possession, possession_team.id)`, contíguos na ordem de `index`; ID de posse que reaparece não é unido. Somente Pass completo/Carry/Shot do titular compõem o denominador ofensivo. Evidências associam até três ações anteriores íntegras; passe incompleto e ações que rompem encadeamento interrompem a associação. `observed_blocks` é média de blocos/jogo; `entry_block_share` e `shot_block_share` são razões agregadas de blocos com entrada no terço/área ou chute. Contexto/relógio/geometria inválidos tornam totais do jogo null; blocos íntegros continuam inspecionáveis. Não representam todas as posses reais, tempo de posse, contra-ataques ou causalidade.

Histórico de atletas valida equipe e escalação da mesma partida; lista alfabética, contagens Pass/Carry/Shot/Pressure, xG e fontes. Denominador individual é jogos com ação selecionada, não minutos. xG ausente em chute atribuído torna acumulado null; roster/associação inválidos excluem ações sem comprovação. Formações iniciais exigem exatamente um Starting XI; frequência divide jogos nessa formação por jogos com formação inicial calculável. Tactical Shift fica separado, sem inferir duração/adequação. Disponibilidade futura é desconhecida.

Regras legadas: `R01_PROGRESSAO` exige entradas adversárias >0 e próprias calculáveis; `R02_PRESSAO_ALTA` exige ao menos 30% da pressão adversária no terço ofensivo e acerto próprio sob pressão; `R03_CHANCES` exige xG favorável adversário >0 e xG contra próprio calculável. Cada perfil e métrica citada precisa de cinco jogos elegíveis. Pode haver zero hipóteses, sem completar quantidade artificialmente.

Apresentação V2.2 suprime conclusões/hipóteses quando qualquer métrica central das duas equipes (`xg_for`, `xg_against`, `shots_for`, `shots_against`, `pass_accuracy`, `final_third_entries`) é ausente/null ou n<5, mantendo valores para consulta descritiva. Isso não reescreve o JSON legado. V3 exige essa suficiência e, em cada métrica citada, valor finito, denominador positivo e n>=5. `V3_ENTRADAS_PASSE`: passes representam >=60% das entradas adversárias; passe/condução devem usar mesmos jogos/exposição. `V3_CHUTES_AREA`: >=60% dos chutes adversários localizados na área, com xG da área e proporção própria calculáveis.

Cinco jogos e limiares 10/30%/60% são escolhas operacionais, sem calibração ou eficácia causal demonstrada. Confiança permanece limitada. xG é qualidade esperada das finalizações, não gol real nem probabilidade de vitória. Pressão e recuperação registradas não medem eficácia; hipóteses exigem vídeo, treino e julgamento humano.

## 5. Contratos JSON e compatibilidade

`AnalysisRequest`: IDs positivos de competição/temporada/equipe/adversário, equipes distintas, exatamente `cutoff_date` ISO ou `target_match_id` válido para o confronto; `recent_matches_window=10` (1–100). Opcionais `venue`, `match_context`, `strategic_objective`, `unavailable_player_ids` e `notes` (até 4.000 caracteres), com valores permitidos no parser/dataclass. A API valida indisponíveis em escalações anteriores da própria equipe.

| Contrato | Campos e invariantes |
|---|---|
| `AnalysisReport`, schema `1.0.0` | `schema_version`, `metadata`, `request`, `team_profile`, `opponent_profile`, `comparison`, `key_findings`, `tactical_hypotheses`, `formation_options`, `lineup_options`, `data_gaps`, `methodology` |
| Perfis legados | `team_id`, `team_name`, `match_ids`, `period_start`, `period_end`, `sample_status`, `metrics`, `quality`; status insuficiente/limitada |
| `MetricEvidence` | `metric_id`, `value`, `unit`, `sample_size`, `match_ids`, `numerator`, `denominator`, `median`, `standard_deviation`, `per_match`, `formula_version`; `per_match` identifica jogo/data/valor/numerador/denominador |
| Hipótese legada | `rule_id`, `recommendation`, `condition`, `evidence_metrics`, `limitations`, `risks`, `preconditions`, `confidence_level` |
| `AnalysisReportV3`, schema `1.1.0` | Subclasse aditiva: somente schema muda e `tactical_v3` é acrescentado; todos os campos legados conservam valores/semântica |
| `tactical_v3` | `formula_version`, `rules_version` (3.0.0), `team_profile`, `opponent_profile`, `metric_definitions`, `hypotheses`, `methodology` |
| Perfis V3 | Identificação/jogos/período, `metrics`, `shots`, `quality`, `sequences`, `sequence_metrics`, `historical` |
| Hipótese V3 | `rule_id`, `title`, `observation`, `action`, `condition`, `evidence_metrics`, `preconditions`, `risks`, `limitations`, `confidence_level` |

`formation_options` e `lineup_options` continuam arrays vazios mesmo com histórico V3. Campos legados de software permanecem `0.1.0`; fórmulas/regras legadas `1.0.0`; extensão `3.0.0`. Não atualizar versões/chaves durante limpeza. `analyze(root, request)` e CLI sem `--v3` preservam schema e baseline byte a byte; `include_v3=True` ativa extensão. JSON usa null e recusa NaN/Infinity. Fontes efetivamente lidas têm caminho relativo e SHA-256; fingerprint é hash do mapa ordenado caminho→hash. Sem timestamp variável de geração. Releitura V3 com fontes/cobertura alteradas causa erro.

`metadata` identifica equipes, referência, amostras solicitadas/analisadas, mando formal quando disponível e fingerprint; `comparison` guarda diferença equipe menos adversário, unidades, amostras e evidências, sem superioridade inferida. `methodology` guarda políticas e fontes lidas; `data_gaps` explicita lacunas. Cada referência em `evidence_metrics` deve resolver um objeto calculável real no JSON. Mudar notas/contexto altera os campos de `request` e, portanto, seus bytes JSON, mesmo sem alterar indicadores/regras; comparação byte a byte com a fixture exige os mesmos parâmetros padrão.

Fixture congelada obrigatória: `outputs/mvp_demo_city_arsenal/report.json`, SHA-256 `424389e2af0afee96eff3d5a7ef79d74f914f12f0965a052d361fe657fd56b08`. Consumidores: `tests/test_local_data.py`, `tests/test_streamlit_ui.py`, `tests/test_v3_integration.py`. Não excluir, mover ou regenerar silenciosamente. Os testes compartilham fixtures Python de `test_managerai` e `test_streamlit_ui`; preservar imports ao renomear módulos.

## 6. Execução

Rodar na raiz, com dados locais provisionados. Exemplos de análise exigem saída **nova**, fora dos brutos. Os caminhos abaixo em `/tmp` são temporários; escolher outro nome se existirem. `--data-root` é opção global, antes do subcomando.

```bash
PYTHONPATH=src python3 -B -m managerai --help
PYTHONPATH=src python3 -B -m managerai --data-root open-data/data catalog
PYTHONPATH=src python3 -B -m managerai teams --competition-id 2 --season-id 27
PYTHONPATH=src python3 -B -m managerai matches --competition-id 2 --season-id 27
PYTHONPATH=src python3 -B -m managerai audit --competition-id 2 --season-id 27
PYTHONPATH=src python3 -B -m managerai analyze --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 --target-match-id 3754314 --output-dir /tmp/managerai-city-v1-01
MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m managerai analyze --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 --target-match-id 3754314 --window 10 --v3 --output-dir /tmp/managerai-city-v3-01
MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m managerai analyze --competition-id 11 --season-id 90 --team-id 220 --opponent-id 217 --target-match-id 3773497 --v3 --output-dir /tmp/managerai-real-v3-01
```

`catalog` reconcilia cobertura/órfãos; `teams` e `matches` listam opções; `audit` abre eventos do recorte inteiro e reporta qualidade, sem certificar semântica completa. `analyze` gera `report.json` e `report.md`; V3 CLI acrescenta `shot_map.png` e `progression_entries.png`. `hypotheses` no stdout conta regras legadas; `v3_hypotheses` conta adicionais. Corte livre: substituir `--target-match-id` por `--cutoff-date 2016-05-08`. Cenário CLI: `--venue`, `--match-context`, `--strategic-objective`, `--unavailable-player-id` repetível, `--notes`. Argumento/erro de dados/opcional ausente retorna código 2; sucesso 0. Diretório existente ou saída dentro dos brutos é recusado.

```bash
MPLCONFIGDIR=/tmp/managerai-mpl venv/bin/python -B -m streamlit run streamlit_app.py
# Dados em outro local:
MANAGERAI_DATA_ROOT=/caminho/open-data/data MPLCONFIGDIR=/tmp/managerai-mpl venv/bin/python -B -m streamlit run streamlit_app.py
```

Abrir `http://localhost:8501`; encerrar com Ctrl+C. Selecionar competição/temporada, equipes, alvo/data e janela; a janela é reativa, fora do formulário. Conferir cobertura, marcar V3 se desejado e enviar o cenário. Prévia verifica calendário/presença de arquivos, sem abrir eventos antes do envio. Mudança de seleção/corte/janela/V3 limpa resultado; cenário manual aplica-se ao reenviar. Downloads JSON/Markdown usam memória, sem sobrescrever saídas. Sem Matplotlib ou recorte auditado, V3 fica desabilitada; núcleo continua disponível.

Não presumir que `venv/` está pronto em outro checkout: validar intérprete e dependências primeiro. Instalação necessária usa os extras acima, definidos no pyproject. A Fase 2 valida o empacotamento em cópia temporária, sem instalar/remover pacotes do ambiente funcional. Instalação em `site-packages` não leva o dataset junto; os exemplos com `PYTHONPATH=src` mantêm a raiz do checkout; fora dele fornecer `--data-root` explícito.

Diagnóstico: `No module named managerai` exige instalação ou `PYTHONPATH=src`; `competitions.json` ausente exige provisionar/configurar dados. Saída já existente exige outro nome, sem apagar resultados. Métrica null exige conferir amostra/denominador, sem substituição implícita. Poucas hipóteses são abstenção legítima; integrações puladas exigem habilitar a variável e conferir opcionais. Confronto sem alvo bloqueia o envio histórico na UI: usar data livre. Catálogo/calendário têm cache de 60 segundos e botão **Atualizar catálogo**; eventos não ficam em cache entre análises. Downloads têm números arredondados apenas na apresentação brasileira; JSON conserva valores exatos. Alterar cenário exige reenviar; mudar janela atualiza prévia e limpa o resultado.

## 7. Testes e avaliação

Resultados reais por fase e comandos exatos estão na seção de validação de [PENDING.md](PENDING.md). Os resultados históricos de 11/10/2026 não substituem execução atual.

```bash
PYTHONPATH=src python3 -B -S -m unittest discover -s tests -v
MANAGERAI_RUN_LOCAL_TESTS=1 MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m unittest discover -s tests -v
PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py
```

`-S` exclui pacotes de site; sem `MANAGERAI_RUN_LOCAL_TESTS=1`, testes reais são pulados. Testes UI/gráficos também dependem dos opcionais. Registrar aprovados, falhas, erros, pulos e versões; pulos não são aprovações. Usar `-B`/`PYTHONDONTWRITEBYTECODE=1`, `TMPDIR`, `MPLCONFIGDIR` e caches XDG em `/tmp` para validações transitórias. A suíte cria fixtures/relatórios/figuras temporários; não modifica brutos. Em tarefa que proíba até temporários, fazer verificações estáticas e declarar a suíte não executada.

| Módulos de teste | Cobertura a preservar |
|---|---|
| `test_managerai.py`, `test_local_data.py` | Contratos, inventário, métricas/qualidade, corte/alvo/futuro, reprodutibilidade e fixture real |
| `test_coverage.py`, `test_v22_presentation.py`, `test_v22_ui.py` | Cobertura, n/período, suficiência e janela reativa |
| `test_presentation.py`, `test_streamlit_ui.py` | Fidelidade numérica, português, UI/CLI e downloads |
| `test_v3_features.py`, `test_v3_rules.py` | Métricas, limites geométricos, denominadores, referências, nulos e abstenção |
| `test_v3_sequences.py`, `test_v3_history.py` | Blocos, temporalidade, atletas/formações e associação verificável |
| `test_v3_integration.py`, `test_v3_presentation.py`, `test_v3_ui.py` | Schema aditivo, integridade entre leituras, CLI/figuras e UI V3 |

Antes/depois de limpeza aprovada: conferir imports, caminhos, links, hashes, fixture congelada, mesmos campos legados com V3, hipóteses rastreáveis e recusa de sobrescrita. Cenários: City 10/10; Real 1/10; primeira data n=0; janela 1; campo ausente; V3 desativada e recorte não auditado. Conferência independente cobre oito métricas em dois jogos, não auditoria estatística total. Streamlit AppTest não substitui revisão humana de navegador/acessibilidade.

Revisão esportiva ainda pendente: registrar hipótese/confronto/corte/versões/fingerprint/avaliador/data/função; classificar sustentada/parcial/não sustentada/não avaliável, com justificativas, desacordos e lances-fonte. Avaliar correção factual, rastreabilidade até eventos/vídeo, compreensão, plausibilidade, condições/riscos e utilidade separadamente. Conferir os cinco jogos por métrica e diferenças de adversários/períodos; verificar se o técnico usaria, adaptaria ou descartaria a sugestão e quais lacunas impedem sua emissão. Definir comportamento e medição do treino antes de selecionar exemplos. Opinião favorável não vira acurácia nem prova causal.

Antes de ML/fine-tuning: definir tarefa/alvo, rótulos, avaliadores/concordância, direitos de uso, exemplos independentes, baseline e métricas; separar por partida e cronologia, só com features anteriores ao alvo, evitando o mesmo jogo nos dois lados da divisão. Os 760 pares equipe/jogo de 380 jogos não são 760 exemplos independentes. Placar ou relatório gerado pelas regras não é rótulo de tática ideal. Somente avaliar adoção após ganho mensurável e independente; nenhuma etapa de treinamento foi implementada.

## 8. Política operacional e transição documental

Documentos operacionais: `AGENTS.md` (regras), este arquivo (estado/contratos/procedimentos) e `PENDING.md` (prioridades/status/decisões). README permanece porta de entrada. Após fase concluída, atualizar estado e pendências com evidências reais; proposta não equivale a implementação.

Não carregar automaticamente `open-data/`, `venv/`, caches, Parquets, notebook/outputs EDA ou JSONs V3 extensos. Consultar catálogo, código/testes da tarefa e trechos específicos. Temporários em `/tmp/managerai-*`; resultados duráveis em novo diretório explicitamente escolhido. Não existe ainda política `.gitignore` para novas execuções: `*.log` oculta inclusive evidências de validação; não adicionar regra ampla para `outputs/`.

As definições operacionais dos dez contratos/guias B1 foram revisadas na Fase 2 e consolidadas aqui, incluindo campos dos dados, diagnóstico, reprodução e protocolo de avaliação. Os dez documentos e os 27 exemplos redundantes B2/B3 foram removidos após migrar os consumidores, conforme `PENDING.md`; os dois requirements paralelos também saíram.

Na Fase 3, os 29 arquivos históricos C foram removidos exclusivamente conforme o manifesto, após validar backup permanente, hashes e extração em pasta temporária nova. O acervo está em `/home/marcos-junior/ManagerAI-backups/`: `ManagerAI-history-13c50e5-20261017.tar.gz` preserva o início da Fase 2 e `ManagerAI-history-phase3-13c50e5-20261017.tar.gz` preserva exatamente os 29 arquivos antes da retirada. Os três documentos que tiveram destinos de links migrados estão preservados nos dois estados; nenhum resultado científico foi reescrito. Manifesto executado, checksums, resultados e recuperação seletiva estão em `PENDING.md`, §§4, 5 e 8. O backup local permanente não implica cópia externa redundante nem acesso automático de outros integrantes.

Iniciar tarefas somente por `AGENTS.md`, este documento e `PENDING.md`; README é guia rápido. Consultar o acervo somente sob demanda, em extração separada, sem converter requisitos antigos em instruções vigentes. Código, testes, contratos, exemplos finais, fixture, verificadores, dados/EDA e snapshot de dependências EDA foram preservados. As funcionalidades e limitações descritas acima não mudaram com a limpeza; outras pendências não foram executadas.
