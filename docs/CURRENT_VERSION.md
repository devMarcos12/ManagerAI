# ManagerAI — estado operacional atual

**CORE-00: V4.1, A/B e C versionadas; instalação e 237 testes validados em checkout limpo. CI e integração Git registradas na seção CORE-00 ao final. O runtime do treinador permanece determinístico; regressões são experimentais.**

Verificado no código em 17/10/2026; Ancestral publicado da integração `e91e55dd51081bd381f69097353ec86ca5bf7583`; HEADs anteriores nos registros de validação são históricos. Este documento reúne o estado vigente. Leia também [PENDING.md](PENDING.md) para prioridades, validação desta fase e manifesto de limpeza. O [README](../README.md) continua como apresentação e guia rápido. Specs, changelogs e relatórios de entrega são referências históricas, sem autoridade para autorizar novas ações.

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
| Infraestrutura de motores V4.1 | Contratos tipados, snapshot imutável, adaptador determinístico e seleção/comparação explícita pela API Python; §9 |
| Regressões experimentais pré-jogo V4.3-A/B | Dataset e avaliação offline implementados; OLS e Ridge ajustadas para prever chutes; §11 |
| Robustez V4.3-C | Walk-forward e ablações offline implementados; sem confirmação independente de superioridade; §12 |
| Motor de IA especializado integrado ao runtime, fine-tuning e LLM | **Não implementados**; experimento quantitativo permanece separado |
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
| `tactical_engine_schema.py`, `tactical_engines.py` | Contratos V4.1 separados, evidências imutáveis, validação e adaptação/seleção de motores sobre relatório já calculado |

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
| `python -m pip install '.[experiments]'` | NumPy 2.5.2, regressões e avaliação experimental |
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
| `test_tactical_engines.py` | V4.1: adaptação real/sintética, validação temporal/estrutural, isolamento, abstenção, seleção e compatibilidade dos três relatórios preservados |

Antes/depois de limpeza aprovada: conferir imports, caminhos, links, hashes, fixture congelada, mesmos campos legados com V3, hipóteses rastreáveis e recusa de sobrescrita. Cenários: City 10/10; Real 1/10; primeira data n=0; janela 1; campo ausente; V3 desativada e recorte não auditado. Conferência independente cobre oito métricas em dois jogos, não auditoria estatística total. Streamlit AppTest não substitui revisão humana de navegador/acessibilidade.

Revisão esportiva ainda pendente: registrar hipótese/confronto/corte/versões/fingerprint/avaliador/data/função; classificar sustentada/parcial/não sustentada/não avaliável, com justificativas, desacordos e lances-fonte. Avaliar correção factual, rastreabilidade até eventos/vídeo, compreensão, plausibilidade, condições/riscos e utilidade separadamente. Conferir os cinco jogos por métrica e diferenças de adversários/períodos; verificar se o técnico usaria, adaptaria ou descartaria a sugestão e quais lacunas impedem sua emissão. Definir comportamento e medição do treino antes de selecionar exemplos. Opinião favorável não vira acurácia nem prova causal.

Antes de ML/fine-tuning: definir tarefa/alvo, rótulos, avaliadores/concordância, direitos de uso, exemplos independentes, baseline e métricas; separar por partida e cronologia, só com features anteriores ao alvo, evitando o mesmo jogo nos dois lados da divisão. Os 760 pares equipe/jogo de 380 jogos não são 760 exemplos independentes. Placar ou relatório gerado pelas regras não é rótulo de tática ideal. Somente avaliar adoção após ganho mensurável e independente; nenhuma etapa de treinamento foi implementada.

## 8. Política operacional e transição documental

Documentos operacionais: `AGENTS.md` (regras), este arquivo (estado/contratos/procedimentos) e `PENDING.md` (prioridades/status/decisões). README permanece porta de entrada. Após fase concluída, atualizar estado e pendências com evidências reais; proposta não equivale a implementação.

Não carregar automaticamente `open-data/`, `venv/`, caches, Parquets, notebook/outputs EDA ou JSONs V3 extensos. Consultar catálogo, código/testes da tarefa e trechos específicos. Temporários em `/tmp/managerai-*`; resultados duráveis em novo diretório explicitamente escolhido. A política atual ignora `open-data/` e `outputs/runs/`, sem ignorar outputs inteiro. `*.log` também oculta evidências locais; não confundir arquivos ignorados com evidências versionadas.

As definições operacionais dos dez contratos/guias B1 foram revisadas na Fase 2 e consolidadas aqui, incluindo campos dos dados, diagnóstico, reprodução e protocolo de avaliação. Os dez documentos e os 27 exemplos redundantes B2/B3 foram removidos após migrar os consumidores, conforme `PENDING.md`; os dois requirements paralelos também saíram.

Na Fase 3, os 29 arquivos históricos C foram removidos exclusivamente conforme o manifesto, após validar backup permanente, hashes e extração em pasta temporária nova. O acervo está em `/home/marcos-junior/ManagerAI-backups/`: `ManagerAI-history-13c50e5-20261017.tar.gz` preserva o início da Fase 2 e `ManagerAI-history-phase3-13c50e5-20261017.tar.gz` preserva exatamente os 29 arquivos antes da retirada. Os três documentos que tiveram destinos de links migrados estão preservados nos dois estados; nenhum resultado científico foi reescrito. Manifestos históricos, checksums e recuperação seletiva estão descritos em `PENDING.md`, §2; validação V4.1 no §6. O backup local permanente não implica cópia externa redundante nem acesso automático de outros integrantes.

Iniciar tarefas somente por `AGENTS.md`, este documento e `PENDING.md`; README é guia rápido. Consultar o acervo somente sob demanda, em extração separada, sem converter requisitos antigos em instruções vigentes. Código, testes, contratos, exemplos finais, fixture, verificadores, dados/EDA e snapshot de dependências EDA foram preservados. As funcionalidades e limitações descritas acima não mudaram com a limpeza; outras pendências não foram executadas.

## 9. Infraestrutura de motores V4.1

Implementada em dois módulos novos, somente com biblioteca padrão; HEAD de entrada `09b73b75c74266347a2f924a67dc95d7c803720f`. A camada recebe `AnalysisReport`/`AnalysisReportV3` **já calculado**, sem alterar o pipeline, os schemas 1.0.0/1.1.0, indicadores, regras, CLI ou Streamlit. A V4.1 não introduziu treinamento, modelo especializado, fine-tuning, LLM ou recomendação de escalação. As regressões posteriores da V4.3-A/B estão separadas no §11. `4.1.0` identifica o contrato/adaptador, não substitui as versões legadas de software/fórmulas/regras.

```text
pipeline.analyze → relatório legado intacto → build_engine_input
  → TacticalEngineInput imutável, sem hipóteses baseline
  → TacticalEngine.analyze → TacticalEngineOutput separado
       ↑ DeterministicEngine copia hipóteses reais do relatório
compare_engines: seleção explícita, mesma entrada, nenhuma classificação de mérito
```

| Contrato / API | Conteúdo e significado |
|---|---|
| `TacticalEngineInput` | `AnalysisRequest` original (IDs, alvo ou corte livre e contexto declarado), data do corte, perfis calculados, qualidade/lacunas e proveniência. `profiles` reutiliza `TeamProfile`/campos `MetricEvidence`; V3 acrescenta indicadores e três métricas agregadas de sequências. Sem eventos brutos, placar do alvo, roster, sequências extensas ou hipóteses geradas |
| `provenance` | Schema/software/fórmulas/regras de origem, políticas temporal/janela, fontes relativas e SHA-256, fingerprint legado; V3 mantém suas fontes/fingerprint e versões próprias |
| `input_fingerprint` | SHA-256 canônico de toda a entrada, incluindo contexto, indicadores e proveniência. Diferente do fingerprint legado, que identifica somente o mapa de fontes |
| `sufficiency` | Reutiliza `coverage.report_sufficiency`: mínimo operacional de cinco partidas calculáveis em cada métrica central das duas equipes; não confiança estatística |
| `EngineHypothesis` | ID/origem, ação e condição já existentes, referências de evidência, riscos, limitações e pré-condições. `title`/`observation` opcionais preservam esses campos V3; ausência significa que a fonte não os forneceu. Não há campo de probabilidade nem confiança inventada |
| `TacticalEngineOutput` | Motor/versão, fingerprint da entrada, proveniência, suficiência e estado `hypotheses`, `no_hypotheses` ou `abstained`, hipóteses e limitações. `.validate_for(inputs)` confere vínculo, evidências calculáveis e amostras |
| `TacticalEngine` | `Protocol` com `engine_id`, `engine_version` e `analyze(inputs)`. Futuras implementações são fornecidas explicitamente ao registro local de `compare_engines`, sem editar o pipeline legado |

`profiles`/`provenance` são cópias recursivas de leitura: objetos viram mappings imutáveis e arrays viram tuplas. `.to_dict()` devolve cópia serializável; não usar `dataclasses.asdict` no snapshot com mappings imutáveis. Não há timestamp/seed aleatória ou escrita em disco na infraestrutura. O adaptador é vinculado ao fingerprint de uma análise e copia as hipóteses existentes, sem reexecutar regras/indicadores nem reler fontes. A entrada oferecida a futuros motores não inclui as hipóteses baseline, evitando que virem rótulos/atributos por acidente.

Exemplo na raiz, com dados previamente provisionados (reutilizar um relatório existente quando disponível):

```python
from managerai.pipeline import analyze
from managerai.report_schema import AnalysisRequest
from managerai.tactical_engines import build_engine_input, compare_engines, DeterministicEngine

request = AnalysisRequest(2, 27, 36, 1, target_match_id=3754314)
report = analyze("open-data/data", request, include_v3=True)
inputs = build_engine_input(report)
baseline = DeterministicEngine(report)
output = baseline.analyze(inputs)
# Alternativa com seleção explícita; o único motor incluído é o determinístico:
outputs = compare_engines(report, engine_ids=("deterministic",))
payload = outputs[0].to_dict()  # resultado separado; report.to_json() não muda
```

Um motor futuro deverá implementar o protocolo e ser passado em `engines=(motor,)`, com seu ID em `engine_ids`. O ID `deterministic` é reservado. ID desconhecido lança `EngineUnavailableError` antes de executar motores; erros de execução/contrato são propagados, sem fallback silencioso. Saídas precisam identificar motor/versão corretos, a mesma entrada/proveniência e referências válidas. Esse mecanismo prepara a comparação controlada, mas **não implementa benchmark esportivo, modelo ou ranking automático**.

Diferença de suficiência preservada: regras legadas podem emitir hipóteses com suas métricas elegíveis mesmo quando faltam métricas centrais. O adaptador se abstém nesse caso, seguindo a política existente da apresentação. As hipóteses brutas e demais campos continuam no JSON legado, sem alteração. `no_hypotheses` significa evidência central disponível sem hipótese emitida; `abstained` significa abstenção, também permitida a futuros motores quando a evidência central é suficiente mas suas próprias exigências falham. Nenhum dos estados equivale a "nenhum risco tático".

Validação estrutural: IDs/equipes/janela, amostras por métrica/partida, valores finitos, datas anteriores ao dia inteiro do corte, alvo ausente, fontes/fingerprints e cobertura V3 compatíveis. Calendário inteiro continua fonte legítima; seu hash não expõe placar futuro como atributo. Escalações de partidas selecionadas sem eventos podem constar das fontes pela validação manual de indisponíveis. O contrato não reabre o calendário para certificar esses casos, não comprova a data de disponibilidade de revisões StatsBomb nem demonstra integridade contra um produtor malicioso; recebe relatórios do pipeline confiável. Fine-tuning sequencial poderá exigir outro contrato de tarefa/eventos, sem ampliar silenciosamente os schemas legados.

Testes históricos V4.1 estão no §6 de `PENDING.md`; V4.2 nos §§7–13, A/B no §14, C no §15 e CORE-00 no §16. Previsão estatística permanece separada da utilidade de recomendações.

## 10. Disponibilidade e limitações dos dados confirmadas na V4.2

Estudo de viabilidade documental concluído, sem treinamento, novo pipeline de atributos, alterações de contratos ou ampliação dos recortes V3. Inventário detalhado, amostragem, comparação de tarefas/modelos, protocolo e condições V4.3 estão em `PENDING.md`. Na V4.2 nenhum treinamento foi executado; as regressões experimentais posteriores estão no §11. O runtime continua sem modelo aprendido integrado, fine-tuning ou LLM.

Inventário atual conferido por `data_inventory.inventory`/`load_season`, lendo catálogo e 80 calendários, sem abrir integralmente os eventos: **24 competições, 80 pares e 3.961 partidas**, entre 24/06/1958 e 27/07/2025. Arquivos de eventos/escalações estão presentes para todas as partidas catalogadas; 426 têm arquivo 360 (10,75%). Há 4.235 arquivos de eventos e 4.235 de escalações, com 274 IDs não vinculados ao catálogo em cada conjunto. Presença não certifica integridade dos conteúdos, calculabilidade de indicadores ou adequação científica. Os pares incluem masculino, feminino e juvenil, clubes/seleções e versões de anotação distintas; não constituem corpus homogêneo por quantidade de eventos.

| Recorte atual | Distribuição e limite confirmado |
|---|---|
| PL 2015/16 `(2,27)` | 380 jogos, 20 equipes com 38 cada. Até 330 alvos com cinco jogos anteriores de ambas as equipes, ou 280 com dez, estritamente antes do dia-alvo. São tetos do calendário/presença, não contagem de exemplos com todas as features/labels certificadas nem independência estatística |
| La Liga 2020/21 `(11,90)` | 35 jogos: Barcelona em todos, 17 adversários em dois e Elche em um; 19 equipes. Nenhum alvo com cinco anteriores de ambas. O recorte sustenta o caso de abstenção, não um experimento bilateral equivalente à PL |

Amostra determinística de 12 jogos (quatro posições cronológicas em PL2015/16, LaLiga2020/21 e WSL2018/19): `match_features` passou nas 12 partidas; contagens diretas de Shot nos períodos1/2 coincidiram por equipe com o núcleo. Nos 43.962 eventos amostrados, 270 chutes tinham xG/localização válidos; 12.382 passes tinham destino válido. Havia 1.941 passes com pressão True, nenhum False explícito e 10.441 sem marcação, que permanecem distintos de False. Isso não valida integralmente outros jogos nem certifica semântica de eficácia tática.

Dois arquivos 360 amostrados tinham frames vinculados por UUID, mas não em todos os eventos: 3.914/4.342 e 3.853/4.205, com 6–21 e 3–22 jogadores por frame. As chaves observadas são `event_uuid`, `freeze_frame`, `visible_area`, e jogadores com `actor`, `keeper`, `location`, `teammate`. Não representam tracking contínuo com velocidades e cobertura garantida de todos os atletas. A V3 continua sem consumir 360.

Foram consultados os metadados dos sete Parquets finais da EDA e somente colunas selecionadas da tabela de 760 linhas equipe/partida (380 grupos). Os 1.313.773 eventos EDA não foram carregados para o estudo. Contagens de linhas e ausência de nulos de chutes/xG nessa tabela são evidência histórica, não rótulos atuais certificados automaticamente: definições/exposição/agregações da EDA diferem do núcleo. Dados originais, lotes, scripts e resultados foram preservados.

Metadados locais incluem `data_version` 1.0.2/1.0.3/1.1.0, diferentes campos de fidelidade e objetos vazios. `match_date` é data de realização; `last_updated` pode ser anos posterior e não prova publicação original. Um backtest neste snapshot pode excluir partidas futuras, mas não reconstruir integralmente a base disponível naquele dia. Proveniência exige commit/hash e explicitação dessa limitação, além de corte temporal; não usar placar, eventos ou formação executada do alvo como features pré-jogo.

O PDF local `open-data/LICENSE.pdf` (User Agreement, atualização indicada 08/09/2023) contém restrições de distribuição/reprodução/fornecimento e exploração comercial (cláusulas1.2/7), além de atribuição com logo (1.4); README também pede atribuição StatsBomb. Não presumir permissões irrestritas de dataset derivado/pesos a partir de licenças de algoritmos. O responsável precisa confirmar a finalidade e autorizações aplicáveis; fontes e lacunas estão em `PENDING.md`, §7.6.

Os snapshots V4.1 preservam agregados e evidências por partida, mas excluem formações/atletas detalhados e `formal_home_team_id`; `request.venue` é declaração manual. A saída V4.1 contém hipóteses/abstenção, sem campo numérico de previsão. Esse limite deve orientar futuros contratos de tarefa/scorer separados; nenhum contrato ou comportamento foi alterado nesta fase.

## 11. Experimento supervisionado V4.3-A/B

Implementação offline opt-in em `src/managerai/experiments/`, fora do pipeline, CLI pública, UI, schemas JSON e adaptador tático V4.1. Há regressões efetivamente ajustadas no experimento; isso não implementa um motor de estratégia ideal, integração LLM, fine-tuning ou escalação. Recorte fixo PL2015/16 `(2,27)`, tarefa `pl_home_shots_pre_match`, versão `4.3-ab.1`. As versões legadas permanecem inalteradas.

| Arquivo / contrato | Responsabilidade |
|---|---|
| `experiments/dataset.py` | Reutiliza `load_season`, `LocalData`, `temporal.select_history` e validação/contagem `match_features`; nenhuma fórmula legada foi modificada |
| `Fixture` | Somente ID, data, mandante/visitante. O calendário é sanitizado, removendo placares e demais campos pós-jogo antes da seleção de históricos |
| `HistoricalEvidence` / `FeatureRow` | Cinco jogos estritamente anteriores de cada equipe, datas, contagens, qualidade e hashes das fontes. `values` tem exatamente dois números; a quantidade de jogos é registrada pelas cinco evidências de cada lado, validada no contrato |
| `build_pre_match_features` | Função pura que recebe somente Fixture e as duas tuplas históricas; não recebe loader, eventos, placar, y ou cache de labels |
| `ObservedLabel` / `Example` / `SupervisedDataset` | y e suas fontes separados de X; uma linha por partida; excluídos com motivos, fontes/hashes e auditoria completa do recorte. Todas as features são congeladas antes da segunda passagem de labels |
| `QuantitativePrediction` | Contrato próprio: tarefa/versão, modelo, partida/data, previsão finita não negativa, fingerprint/fontes dos atributos, suficiência e limitações. Não reutiliza `TacticalEngineOutput`; não produz preenchimento para insuficiência |
| `experiments/models.py` | B0/B1 são regras no avaliador; OLS/Ridge usam NumPy sob demanda. OLS `lstsq` com intercepto; Ridge alpha1 fixo, intercepto não penalizado; z-score populacional ajustado só no treino, constantes com escala1 |
| `experiments/runner.py` | Limites temporais fixos, avaliação sem tuning, métricas/distribuições, previsões por partida e um único `run.json`; entrada separada por `python -m`, sem editar a CLI legada |

**Features:** média de `shots_for` do mandante nos últimos cinco jogos e média de `shots_against` do visitante nos últimos cinco, independentemente do mando histórico desses clubes. Não usa chutes no alvo, xG, times como números ordinais, dezenas de atributos ou dados da partida-alvo. Janela exata5, sem reposição de arquivos faltantes; todo o dia-alvo é excluído. Empates do calendário sanitizado usam `(match_date,match_id)`, sem alegar ordem intradiária verificada. Mando formal define qual clube é o mandante do exemplo, não é uma escalação nem um efeito causal estimado.

**Alvo:** contagem de eventos com `type.id=16` e `type.name='Shot'` do mandante nos períodos1/2, incluindo acréscimos, todos os outcomes e pênaltis regulamentares. Prorrogação/disputa de pênaltis e tipos distintos, como Own Goal Against, não viram Shot. IDs/índices duplicados, incoerência ID/nome, marca explícita de cancelamento ou fluxo inválido bloqueiam, sem deduplicar/corrigir silenciosamente. Zero só após fluxo íntegro sem Shot. A ausência de marca de cancelamento não prova decisões VAR/anulação: mede-se a contagem registrada pelo fornecedor. Escalação ausente não invalida automaticamente contagem coletiva, mas fica registrada; nunca se inventa disponibilidade de atletas.

Construção real: 380 partidas auditadas, 1.313.773 IDs únicos, 9.908 chutes dos dois times; **330 exemplos válidos e 50 excluídos por histórico insuficiente**, 762 fontes SHA-256 (catálogo, calendário,380eventos,380escalações). Duas durações e três coordenadas inválidas e8.077 localizações ausentes ficam na qualidade; não são denominador/entrada do alvo de contagem e não foram corrigidas no bruto. São relevantes para outras análises, sem impedir a contagem validada por tipo/ID. A nova leitura é construção/auditoria específica do dataset, não reexecução dos geradores EDA.

Divisão por datas fixadas antes dos resultados, retomando os blocos propostos na V4.2 com a janela agora **cinco**, conforme autorização atual:

| Partição | Datas-alvo | Exemplos | Equipes |
|---|---|---:|---:|
| Treino | 19/09/2015–06/02/2016 |198|20|
| Validação | 07/02/2016–03/04/2016 |65|20|
| Teste | 09/04/2016–17/05/2016 |67|20|

São blocos de dias inteiros, não meses/rodadas completas nem múltiplas temporadas; não há partidas elegíveis no intervalo entre validação e teste. Não houve escolha de fronteiras pelo erro. Pesos e scaler usam somente198 jogos do treino; validação é apenas avaliação, sem ajuste, seleção de features, tuning ou refit. Histórico prequential incorpora jogos já passados para confrontos posteriores de validação/teste; isso não atualiza pesos/transformadores. Não se embaralha nem se separam equipes/eventos do mesmo jogo entre partições.

B0 prevê média histórica própria; B1 média50/50 própria/ofensiva e adversária/concedida. Todas as previsões seguem `max(0,raw)`, sem arredondar para inteiro; nessa execução nenhuma foi truncada. MAE principal, RMSE, viés `predito−observado` e quantis de erros assinados/absolutos; métricas mensais descritivas só com n>=10. Resultados reais e diferenças contra ambos baselines estão no §14 de PENDING. Nenhum intervalo IID foi calculado e nenhuma superioridade estatística/esportiva foi demonstrada.

**Dependências:** extra canônico `experiments` no `pyproject.toml` contém somente `numpy==2.5.2`, já disponível no venv; nenhuma instalação ocorreu. Núcleo/CLI/UI/V3 continuam com as dependências anteriores. Para outro ambiente, a instalação opcional `.[experiments]` é separada dos extras UI/V3/EDA e deve ser feita somente quando necessária/autorizada.

Execução na raiz, com destino **novo** (o artefato original é preservado):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 venv/bin/python -B -m managerai.experiments.runner --data-root open-data/data --output-dir outputs/runs/v43_ab_nova_execucao
```

Dentro do checkout só são aceitos destinos novos sob `outputs/runs/`; dados, código, docs, testes e saídas protegidas são recusados antes de construir/treinar. É possível reproduzir em pasta temporária nova fora do checkout. Cada execução escreve somente um `run.json`, com dataset/exclusões, protocolo/versões, fonte/hashes, IDs/datas/contagens dos conjuntos, coeficientes/scaler, erros/previsões e contexto Git. Não cria CSV, pickle de modelo ou Markdown operacional paralelo. HEAD sozinho não identifica fontes locais não commitadas: hashes do código e pyproject também são registrados. Metadados de execução, como status Git, podem diferir; dataset, protocolo, coeficientes, métricas e previsões foram reproduzidos exatamente nesta máquina/versões.

Artefato original: `outputs/runs/v43_ab_pl2015_16_20261017/run.json`. Experimento de pesquisa local não comercial, sem publicação/redistribuição; termos StatsBomb continuam aplicáveis a dados/derivados. A data original de disponibilidade das anotações não é reconstruída. Uma temporada/67 jogos de teste e clubes compartilhados limitam generalização; menor erro de chutes não demonstra melhor decisão tática. No encerramento A/B, C ainda não havia sido iniciada; implementação e resultados posteriores no §12.

## 12. Robustez experimental V4.3-C

Dados: **StatsBomb Open Data** — [fonte e termos na revisão utilizada](https://github.com/hudl/open-data/tree/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb). Atribuição com ícone da [organização oficial](https://github.com/statsbomb), verificado em 17/10/2026:

![StatsBomb](https://avatars.githubusercontent.com/u/23416229?s=200&v=4)

Análise offline concluída, sem alterar V3, V4.1, A/B, CLI, UI, schemas, dados ou EDA. O módulo `src/managerai/experiments/robustness.py` reutiliza dataset, contratos e solvers A/B; `robustness_diagnostics.py` calcula comparações pareadas e sensibilidades sem reajuste. Dois módulos novos de testes cobrem 37 casos; não há dependência nova nem alteração do pyproject nesta fase.

**Protocolo:** sete meses completos de novembro/2015 a maio/2016, treinando somente em datas anteriores ao primeiro dia do mês. Esquema expansivo: mínimo 50 exemplos. Sensibilidade separada: últimos 90 dias de treino, mínimo 30. Cada mês exige 20 exemplos avaliáveis; esses limites são guardas operacionais, não poder estatístico. Todos os 14 meses/esquemas passaram. Os 330 exemplos A/B continuam válidos, com os mesmos 50 excluídos; 57 exemplos iniciais só treinam, e **273 partidas únicas** recebem previsão por esquema. São as mesmas partidas nos dois esquemas, não 546 observações independentes.

Pesos, intercepto e scaler são reajustados somente no treino de cada origem e congelados durante o mês; features H5 incorporam somente jogos anteriores ao dia-alvo. Não se separam datas inteiras, não há shuffle/tuning, e validação/teste A/B não são reutilizados como confirmação independente. Todo o estudo C é exploratório pós-A/B; abril/maio contêm o teste já conhecido.

Mantidos B0, B1, OLS e Ridge alpha=1. Controle adicional: média y somente do treino (intercepto). Ablações: somente média ofensiva própria ou somente concedida adversária; coluna removida é zerada antes de scaler/fit/previsão, sem imputar ausência. Não existe feature variável de mando ou grupo complementar no dataset. Todos os modelos avaliam os mesmos IDs, com truncamento `max(0,raw)`; nenhum truncamento ocorreu.

Resultados agregados MAE / RMSE / viés (chutes por jogo; viés=predito−observado):

| Modelo | Expansivo MAE | RMSE | Viés | Móvel90 MAE | RMSE | Viés |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 4.384615 | 5.713822 | -1.971429 | 4.384615 | 5.713822 | -1.971429 |
| B1 | 4.124176 | 5.396909 | -2.015751 | 4.124176 | 5.396909 | -2.015751 |
| Média y do treino | 4.285490 | 5.588999 | -0.645782 | 4.285756 | 5.570507 | -0.476600 |
| OLS | 3.994988 | 5.140741 | -0.973664 | 4.074797 | 5.167582 | -0.599850 |
| Ridge α=1 | 3.995920 | 5.141355 | -0.968684 | 4.073650 | 5.167031 | -0.596517 |
| OLS só próprio | 4.086623 | 5.320034 | -0.793357 | 4.150491 | 5.323408 | -0.502279 |
| Ridge só próprio | 4.087036 | 5.320171 | -0.791468 | 4.149323 | 5.322771 | -0.501451 |
| OLS só adversário | 4.196389 | 5.437409 | -0.751557 | 4.211645 | 5.429816 | -0.498321 |
| Ridge só adversário | 4.196556 | 5.437791 | -0.750544 | 4.211514 | 5.429784 | -0.497933 |

OLS reduz numericamente MAE frente a B1 em 3,1324% no expansivo e 1,1973% no móvel; Ridge em 3,1099% e 1,2251%. OLS/Ridge melhoram 6/7 meses no expansivo e 3/7 no móvel. São resultados exploratórios, sem escolha automática de vencedor: diferença OLS/Ridge inferior a 0,0012 chute/jogo nos agregados.

As duas remoções pioraram MAE agregado, mas não todos os meses; não comprovam contribuição causal nem redundância estável. A vantagem móvel frente a B1 muda de sinal ao excluir fevereiro, maio ou os 14 maiores erros B1. Excluir um único jogo não muda o sinal agregado. Dados, janelas históricas e clubes compartilhados introduzem dependência: nenhum IC/p-valor IID é produzido. Quantis, exposições por equipe, meses e exclusões são diagnósticos descritivos sem refit; as exposições por equipe são sobrepostas. Detalhes, aceite e pendências em PENDING §15.

Reprodução na raiz, exigindo os módulos A/B anteriores, dados locais na revisão registrada e NumPy 2.5.2 já disponível:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 venv/bin/python -B -m managerai.experiments.robustness --data-root open-data/data --reference-artifact outputs/runs/v43_ab_pl2015_16_20261017/run.json --output-dir outputs/runs/v43_c_nova_execucao
```

Destino obrigatoriamente novo; somente `outputs/runs/` dentro do checkout, ou temporário externo. Reconstrução dos brutos e fingerprints congelados impedem continuar silenciosamente diante de divergência. CORE-00 permite novos metadados A/B sem exigir o hash binário histórico; verifica todos os resultados conforme §13. Um único `run.json` C referencia o manifesto A/B e guarda configuração, janelas, IDs, modelos/scalers, previsões, métricas e diagnósticos, sem copiar eventos ou o dataset inteiro. A segunda execução desde os brutos em `/tmp` reproduziu exatamente protocolo, referência e resultados, incluindo coeficientes/previsões. Contexto Git pode diferir e não é feature.

Artefato local: `outputs/runs/v43_c_pl2015_16_20261017/run.json`. `.gitignore` protege `open-data/` e `outputs/runs/`; dados/artefatos permanecem no disco e não são publicados por Git. O A/B original está preservado. O delta C original não incluía seus pré-requisitos locais. **CORE-00 resolveu esse bloqueio**, versionando-os em commits próprios com origem identificada. O clone da integração contém todos os módulos; os dados são externos e o artefato A/B pode ser reconstruído, conforme §13.

Validação: 228 testes completos aprovados, zero falhas/erros/pulos; 16 comparações independentes aprovadas. Sem site-packages: 185 aprovados/43 pulados. Nenhum treinamento complexo, fine-tuning, LLM, recomendação de escalação ou integração no motor tático. Não avançar automaticamente; primeiro obter dados independentes e critério útil pré-fixado. OLS pode continuar referência simples de pesquisa e Ridge controle; não há evidência suficiente para justificar maior complexidade ou superioridade esportiva.

## 13. CORE-00 — instalação, versionamento e integração

V4.1, A/B, C e testes correspondentes estão versionados. Os commits C `a1e3cd1`/`e91e55d` foram preservados como ancestrais; integração em `integration/core-00`, a partir de `e91e55d`. Os nove pré-requisitos locais foram conferidos contra inventários e hashes das sessões anteriores e incluídos separadamente: V4.1 em `d59ba93`, A/B e extra NumPy em `d075d33`. Não houve inclusão de trabalho preexistente de origem desconhecida. Os registros documentais V4.1/V4.2/A/B que permaneciam locais também foram consolidados, sem atribuir seus resultados históricos à CORE-00.

Um checkout limpo foi clonado em `/tmp/managerai-core00-ftkm4jw5/checkout`. Dois ambientes novos, sem herdar site-packages do venv funcional, instalaram `python -m pip install .` e `python -m pip install -r requirements.txt '.[experiments]'`. Imports foram verificados com `-I` a partir do wheel instalado, sem PYTHONPATH original. `pip check` passou nos dois ambientes; versões diretas existentes foram mantidas. O ambiente funcional original não foi alterado. Não existe lock completo de transitivas; as versões resolvidas desta validação ficaram registradas em temporário, não como novo requirements paralelo.

A validação instalada inicialmente encontrou um erro real: os runners confundiam `site-packages` com a raiz do checkout. `experiments/paths.py` agora encontra o checkout pelo `pyproject.toml` de ManagerAI no diretório de execução/ancestrais, com fallback apenas para layout src. Execute os experimentos dentro do checkout. A proveniência usa os bytes do pacote efetivamente executado, inclusive quando instalado, com chaves `src/managerai/...`; Git/pyproject continuam identificando o checkout. Não houve alteração em features, labels, fórmulas ou modelos.

A C também dependia do SHA binário de um A/B histórico não distribuído. Agora aceita A/B reconstruída: protocolo e dataset precisam dos fingerprints congelados exatos; todos os resultados, inclusive previsões/coeficientes/evidências, precisam da assinatura congelada com floats arredondados a oito casas. Essa regra só calcula a assinatura, não arredonda ou modifica resultados armazenados; metadados de ambiente/Git podem variar. O SHA histórico e o novo SHA da referência continuam registrados. Nove testes novos cobrem instalação, proveniência, alterações relevantes de resultados, protocolo/dataset modificados e referência reconstruída. A primeira falha instalada (228 descobertos, um erro e43 pulos) foi corrigida na causa, sem relaxar o teste de proteção de destinos.

Resultados em checkout limpo, com código instalado:

| Execução | Descobertos | Aprovados | Pulados | Falhas/erros |
|---|---:|---:|---:|---:|
| Núcleo instalado, sem opcionais | 237 | 194 | 43 | 0 |
| Biblioteca padrão, `-S`/src | 237 | 194 | 43 | 0 |
| UI/V3/NumPy, sem dados | 237 | 227 | 10 | 0 |
| Completa com dados externos | 237 | 237 | 0 | 0 |
| Verificação independente com dados | 16 | 16 | 0 | 0 |

A CI em [ci.yml](../.github/workflows/ci.yml) executa os perfis core/opcionais em Python3.12/Ubuntu24.04 para PRs e pushes em main. Actions oficiais são fixadas por SHA, permissões somente leitura; verifica wheel/imports, CLI, pip check e contratos pelos testes portáveis. Não recebe StatsBomb nem tenta esconder a ausência dos dez testes reais: esses são validação separada. Não há credenciais, infraestrutura paga ou novas Issues do roadmap.

Provisionamento: obter externamente StatsBomb Open Data, conferir `README.md`/`LICENSE.pdf`, atribuição e revisão `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`, com raiz em `open-data/data/` ou caminho explícito no experimento. Um clone ManagerAI não baixa/redistribui esses dados. Na validação local, somente um symlink ignorado em /tmp referenciou o clone existente. Fixtures congeladas e exemplos finais necessários aos testes permanecem no Git. Fonte/fixture/EDA originais foram preservados; não se executaram geradores EDA.

Reprodução completa a partir do clone e wheel, sem copiar os JSONs de runs históricos:

```bash
python -m pip install -r requirements.txt '.[experiments]'
python -I -B -m unittest discover -s tests -v
MANAGERAI_RUN_LOCAL_TESTS=1 python -I -B -m unittest discover -s tests -v
python -I -B outputs/v22_v3_validation/check_metrics.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -I -B -m managerai.experiments.runner --data-root open-data/data --output-dir outputs/runs/repro_ab
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -I -B -m managerai.experiments.robustness --data-root open-data/data --reference-artifact outputs/runs/repro_ab/run.json --output-dir outputs/runs/repro_c
```

Usar destinos novos. Runs/metadata de execução variam legitimamente; números científicos, protocolo e dados permanecem verificáveis. Todos os módulos estão no clone; dados e runs grandes continuam externos/ignorados. Ciência observacional da C e limites de uma temporada/273 partidas permanecem os do §12. Publicação/CI/PR corrente e comparação da reprodução estão em PENDING §16; nenhuma nova funcionalidade de Core, LLM, fine-tuning ou integração frontend foi implementada.
