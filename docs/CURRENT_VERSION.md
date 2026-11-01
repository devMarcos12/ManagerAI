# ManagerAI — estado operacional atual

Atualização de 01/11/2026: entrada por equipe implementada sobre
[`cccd25f`](https://github.com/devMarcos12/ManagerAI/commit/cccd25ff352ae5a2b7a85f6249b8c161f86b6a60).
Regras de trabalho em [AGENTS.md](../AGENTS.md), prioridades/evidências em
[PENDING.md](PENDING.md) e instalação rápida no [README](../README.md).
Resultados de testes identificam o ambiente e não garantem validade esportiva.

Limpeza aprovada de gerados concluída neste checkout: 59 arquivos de build/metadados e bundle web removidos (693.739 bytes), com rollback conferido. Código, testes, dados e fixtures preservados. Detalhes em [PENDING.md](PENDING.md#6-manifesto-da-limpeza). Arquivos ignorados em outra máquina não são apagados por git pull; um novo build pode recriá-los.

## 1. Produto e fronteiras

ManagerAI apoia preparação pré-jogo com histórico local StatsBomb Open Data. Calcula indicadores e hipóteses condicionais por regras. A interface React usa a API FastAPI local; CLI e Streamlit continuam disponíveis. O núcleo analítico funciona sem rede, LLM ou GPU após provisionar dados/dependências. Não há motor tático aprendido, escalação ideal, previsão de vitória ou eficácia causal demonstrada.

| Capacidade | Estado vigente |
|---|---|
| Seleção temporal, métricas, qualidade e proveniência | Núcleo determinístico, schema 1.0.0 |
| CLI, JSON/Markdown e Streamlit | Implementados e preservados |
| Extensão V3 | Opt-in; 26 indicadores, três agregados de sequências, histórico de atletas/formações e dois gráficos |
| V3 certificada | Somente Premier League 2015/16 `(2,27)` e La Liga 2020/21 `(11,90)` |
| Infraestrutura V4.1 | Snapshot imutável e adaptador determinístico; saídas separadas do relatório legado |
| Serviço/API 2.0.0 e frontend React | Planos condicionais, restrições, evidências e exportação local |
| Filtros por indicador | `quality_v1`, opt-in somente na análise básica do serviço/API/frontend |
| LLM explicadora | Ollama opcional para seleção validada de afirmações; texto final materializado pelo Core |
| Regressões OLS/Ridge e LoRA de explicação | Experimentos offline; não promovidos à decisão de produção |
| Tracking/360 analítico e recomendação individual | Não implementados |

Contexto, objetivo, mando e elenco são declarações do treinador, com validações. No legado, não mudam métricas/gatilhos. No serviço, estratégia e objetivo apenas ordenam planos já sustentados por mapas explícitos; restrições podem removê-los. Histórico de atleta/formação não demonstra disponibilidade atual nem adequação tática. Evidência insuficiente produz abstenção.

### Entrada por equipe — 01/11/2026

A web começa por busca global do time, data de corte e janela padrão dez.
Competição/temporada são identificadas e exibidas; sobreposição exige desempate
explícito. O panorama individual (`team-overview-1`) reutiliza seleção temporal
e os 21 indicadores básicos, sem adversário fictício ou planos. Mostra amostra,
lacunas, fontes, valores ausentes e exportação JSON. Usa política básica `legacy`,
sem filtros por família/V3/LLM; isso acompanha o resultado. Contexto opcional e
comparação ficam disponíveis ao adicionar adversário da mesma temporada.

`coach_service.py` fornece índice por equipe, prévia e análise individual;
`GET /v1/coach/teams`, `POST /v1/team-coverage` e `POST /v1/team-analyses` são
aditivos ao contrato HTTP 2.0.0. O índice lê somente metadados/presença de arquivos.
Datas antigas e lacunas aparecem na interface; calendário não comprova situação
atual. Referência por partida preenche mando formal automaticamente, sem inferir
campo neutro. Extensão V3, filtros de qualidade, restrições e explicação permanecem
em opções adicionais da comparação. CLI/Streamlit e fórmulas não foram alterados.

Validação desta entrega e limites do ambiente: [PENDING](PENDING.md#8-validação-da-entrada-por-equipe).

## 2. Arquitetura e módulos

`pipeline.analyze` carrega catálogo/calendário, seleciona históricos, calcula perfis/comparações/regras e produz o relatório legado. `include_v3=True` estende esse resultado. `service.build_service_report` aplica contexto/restrições e, quando solicitado, a projeção de qualidade; só depois oferece afirmações à explicação opcional. A API expõe esse serviço e o frontend apresenta o resultado tipado.

Todos os módulos abaixo ficam em `src/managerai/`.

| Módulos | Responsabilidade |
|---|---|
| `cli.py`, `__main__.py`, `__init__.py` | Comandos locais, entrada e versão |
| `data_loader.py`, `data_inventory.py`, `temporal.py` | Leitura com SHA-256, catálogo e seleção temporal |
| `feature_engineering.py`, `tactical_analysis.py`, `recommendation_engine.py` | 21 indicadores, comparações e três regras básicas |
| `report_schema.py`, `pipeline.py`, `report_renderer.py` | Contratos, orquestração e Markdown |
| `coverage.py`, `sufficiency.py`, `presentation/` | Prévia de presença, suficiência compartilhada, terminologia e apresentação |
| `ui_support.py`, `streamlit_ui.py` | Seletores/erros e UI Streamlit; entrada em `streamlit_app.py` |
| `v3_schema.py`, `v3_pipeline.py`, `v3_features.py`, `v3_rules.py` | Extensão, allowlist, métricas e regras V3 |
| `v3_sequences.py`, `v3_history.py`, `v3_presentation.py`, `v3_plots.py` | Sequências, histórico, apresentação e gráficos |
| `tactical_engine_schema.py`, `tactical_engines.py` | Contratos imutáveis e seleção explícita de motores V4.1 |
| `service_schema.py`, `service.py`, `options.py`, `explanation.py` | Contexto, planos, opções canônicas e explicação validada |
| `http_schema.py`, `api.py` | HTTP/OpenAPI tipados e retenção volátil de relatórios |
| `metric_eligibility.py`, `quality_report.py` | Dependências por família e projeção opt-in no serviço |
| `statsbomb_provisioning.py`, `statsbomb_snapshot.json`, `season_audit.py` | Contrato de fonte, verificação e auditoria sem promoção automática |
| `experiments/` | Dataset, regressões, robustez e pesquisa de explicação, separados do runtime tático |

`streamlit_app.py` adiciona `src/` ao caminho; a API deve usar o pacote instalado atualizado. Imports de V3/gráficos/NumPy são opcionais conforme o módulo. `v3_rules.py` reutiliza `sufficiency.py`; apresentação/cálculo ainda compartilham alguns helpers. Os scripts EDA têm destinos históricos fixos e não são testes rotineiros: preservar `run_statsbomb_eda.py`, `finalize_statsbomb_eda.py` e `gerar_docx_eda.py` sem executá-los para limpeza.

## 3. Ambiente, dados e temporalidade

Python `>=3.12`; [pyproject.toml](../pyproject.toml) é a fonte canônica de dependências. Núcleo com `dependencies=[]`. `requirements.txt` seleciona `.[v3]`. Extras: `ui` (Streamlit), `v3/dev` (Streamlit/Matplotlib), `api` (FastAPI/Uvicorn/HTTPX), `experiments` (NumPy), `training` (Transformers/PEFT/PyTorch) e `eda` (ferramentas de pesquisa). Pins diretos não são lock completo de transitivas. O snapshot em `docs/history/requirements-eda-20261017.txt` é histórico, sem autoridade de instalação atual.

Frontend: Node compatível com `frontend/.nvmrc` e `package.json` (20.19+ ou 22.12+), `npm ci` com lockfile versionado. React/ReactDOM são as dependências de runtime; build/tipos/testes usam TypeScript/Vite/Playwright. Não instalar treinamento para executar a web.

Dados são externos ao Git principal: `open-data/data/` ou raiz explícita com `competitions.json`, `matches/`, `events/` e `lineups/`. `three-sixty/` é inventariado, sem consumo analítico. `data/raw/` e `data/processed/` são placeholders. Revisão contratada `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`; clone novo do ManagerAI não inclui StatsBomb. Provisionamento, licença e comportamento do verificador em [STATSBOMB_PROVISIONING.md](STATSBOMB_PROVISIONING.md).

A análise usa uma competição/temporada e os históricos das duas equipes, incluindo seus jogos contra outros clubes. Janela padrão dez; núcleo aceita 1–100, web/API 1–20. Só entram datas anteriores ao dia do corte; alvo, todo o dia de referência e futuro são excluídos. A janela não é ampliada para repor arquivos ausentes ou jogos bloqueados, nem mistura temporadas. Apenas períodos 1/2, com acréscimos; prorrogação/disputa de pênaltis ficam fora dos indicadores.

`--data-root` prevalece sobre `MANAGERAI_DATA_ROOT`. Para pacote instalado, usar raiz explícita, evitando inferir dados dentro do ambiente Python. `verify-data` confere revisão/origem/controles/calendários e presença, sem hashear todos os eventos. Diagnóstico de conteúdo parcial não substitui esse gate. Preservar JSONs, README/licença/atribuição StatsBomb e EDA; não corrigir brutos para fazer um indicador passar.

## 4. Métricas e interpretação

Somente períodos 1 e 2. Exposição = soma dos maiores `timestamp + duration` de cada tempo / 60, incluindo acréscimos; não somar `minute` novamente e não chamar de tempo de bola em jogo. Plano StatsBomb 120×80, sem unidade de metros. Área: `x>=102` e `18<=y<=62`; terço final começa em `x=80`. Faixas y: `<80/3`, `[80/3,160/3)`, `>=160/3`. V3 usa meta de referência `(120,40)`, direção x crescente assumida nos dois recortes da allowlist vigente; a guarda operacional não certifica a direção de cada evento; não espelha períodos nem interpreta faixas y como esquerda/direita tática.

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

## 6. Serviço, qualidade e motores

O [contrato HTTP](BACKEND_API.md) é `2.0.0`, com `legacy_report` intacto, `evidence`, `sufficiency`, `plans`, restrições, comparação descritiva e explicação opcional. Contexto não estima ganho esperado. O único motor público selecionável é `deterministic`; indisponibilidade/combinação inválida gera erro explícito, sem troca silenciosa.

`data_policy="legacy"` é o padrão e mantém a suficiência de seis indicadores centrais. `quality_v1` aplica dependências das famílias aos 21 indicadores básicos ativos, preservando o resultado original em `legacy_report`. A projeção reagrega evidências por somas, mantém nulo/zero/fórmulas e regenera regras com evidências utilizáveis. `data_quality` informa 42 combinações indicador/equipe, amostra original/utilizável/selecionada, exclusões, motivos e fingerprint. Famílias exigem todos os seus indicadores ativos calculáveis; o aproveitamento é conservador.

A suficiência de `quality_v1` exige cinco jogos nas duas equipes para `xg_for`, `xg_against`, `shots_for`, `shots_against` e `pass_accuracy`; cada regra mantém seus requisitos próprios. Não combina com V3. Famílias direcionais ficam bloqueadas fora da allowlist existente, ainda que a guarda local seja coerente. Releitura limitada ao histórico selecionado confere hashes contra o relatório original e recusa mudança de fonte. `full_snapshot_status="not_checked"`; não há nova certificação. O contrato separado é `service-quality-1`, motor de proveniência `deterministic-quality`, versão `quality-report-1`; isso não amplia V4.1 ou schemas legados.

Na V4.1, `build_engine_input` cria cópia recursivamente imutável com indicadores/contexto/fontes, sem hipóteses baseline ou eventos brutos; `compare_engines` compartilha esse snapshot entre motores explicitamente registrados. `DeterministicEngine` copia hipóteses reais do relatório, sem recalcular features/regras. `.validate_for(inputs)` confere identidade, proveniência, amostras e referências. `abstained`, `no_hypotheses` e `hypotheses` são estados distintos. Registro desconhecido falha; o contrato não prova integridade de produtor malicioso, disponibilidade histórica de anotação ou validade esportiva.

API local de um worker, sem banco/fila/autenticação multiusuário; retenção em memória e exportação podem expirar. Não expor publicamente sem implantação própria. Frontend React apresenta evidências e gráficos sob demanda, preserva o pedido enviado e não faz retry automático. Datas de calendário não são deslocadas por fuso. Não grava notas/relatórios em localStorage. OpenAPI e tipos/opções gerados são versionados; `options.py` define as opções canônicas.

LLM fica desativada por padrão. Ollama opcional seleciona IDs de afirmações autorizadas; o Core materializa o texto em português, mantendo evidências e condições. Texto livre/IDs extras/omissões são recusados. Modo `optional` preserva o relatório em falha; `required` retorna erro. O ajuste experimental de explicação e as regressões não são usados como motor tático. Protocolo, decisões e resultados em [PENDING.md](PENDING.md#4-ia-e-decisões-científicas).

## 7. Execução e validação

Instalação e início conjunto da web: [README](../README.md#aplicação-web-local). Não presumir `venv/` ou `.venv-web/` pronto nem substituir ambiente funcional. Depois de atualizar código do backend, reinstalar o pacote no ambiente usado pelo servidor. API/explicação/contratos e testes reais de navegador: [BACKEND_API.md](BACKEND_API.md). CLI/Streamlit: [README](../README.md#executar).

Na raiz, com destino de análise novo e dados provisionados:

```bash
PYTHONPATH=src python3 -B -m managerai --help
PYTHONPATH=src python3 -B -m managerai --data-root open-data/data verify-data
PYTHONPATH=src python3 -B -m managerai --data-root open-data/data analyze --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 --target-match-id 3754314 --output-dir /tmp/managerai-city-novo
```

`analyze` gera JSON/Markdown; `--v3` acrescenta os dois gráficos quando opcionais/recorte permitem. `catalog`, `teams`, `matches` e `audit` são comandos separados; auditoria não certifica automaticamente. Sucesso retorna 0, erro de argumento/dados retorna 2. Saída existente ou dentro dos brutos é recusada. Root default vem de `cli.DEFAULT_DATA`; preferir raiz explícita nos exemplos instalados.

Comandos de validação, conforme ambiente já preparado:

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -B -S -m unittest discover -s tests -q
.venv-web/bin/python -I -B -m unittest discover -s tests -q
MANAGERAI_RUN_LOCAL_TESTS=1 MPLBACKEND=Agg MPLCONFIGDIR=/tmp/managerai-mpl .venv-web/bin/python -I -B -m unittest discover -s tests -q
.venv-web/bin/python -I -B scripts/export_openapi.py --check
```

O primeiro perfil usa somente biblioteca padrão; o segundo testa pacote instalado, com os opcionais presentes; o terceiro habilita dados reais do clone completo. `MANAGERAI_CORE02_CONTENT_ROOT` habilita os casos específicos da cópia parcial La Liga, sem substituir o opt-in integral. Integração V3/UI requer dependências próprias. O verificador independente `outputs/v22_v3_validation/check_metrics.py` compara 16 casos/métricas com dados completos, sem certificar estatística total. Não foi reexecutado nesta limpeza.

Em `frontend/`: `npm run types:check`, `npm run build` e `npm test`. Navegador portátil usa fixtures sintéticas; casos `*.real.ts` são opt-in, separados, com API instalada/dados/provedor conforme o cenário. `scripts/export_openapi.py` e `npm run types` atualizam contratos; conferir divergências antes da entrega. CI em [.github/workflows/ci.yml](../.github/workflows/ci.yml) testa wheel mínimo, opcionais e frontend em checkout limpo, sem StatsBomb.

Pulos não são aprovações. Registrar intérprete, comandos, aprovados, erros/falhas/pulos e limites, sem reutilizar contagens antigas como execução nova. Temporários/caches em `/tmp/managerai-*`, sem executar geradores sobre saídas congeladas. Preservar todos os testes reutilizáveis e imports compartilhados. Evidências atuais/históricas e escopo efetivamente executado: [PENDING.md](PENDING.md#3-evidências-da-versão-em-uso).

## 8. Pesquisa, evidências e manutenção

Experimentos em `experiments/` usam contratos quantitativos separados, com features históricas congeladas antes de carregar labels, divisão por partida/dia e ajuste de scaler só no treino. OLS/Ridge usam NumPy; A/B e robustez C são pesquisa offline, sem integração à decisão de produção. LoRA usa supervisão sintética de explicação, sem rótulos de tática ideal. Comandos reprodutíveis no [README](../README.md#reproduzir-os-experimentos) e no [guia da API](BACKEND_API.md); destinos sempre novos sob `outputs/runs/` ou temporário externo permitido.

Resultados/limites essenciais e ponteiros para acervo completo ficam em [PENDING.md](PENDING.md). [research_evidence.json](research_evidence.json), [core_ai_protocol.json](core_ai_protocol.json), [tactical_review.schema.json](tactical_review.schema.json), [season_coverage_core02.json](season_coverage_core02.json) e [core02_laliga_201516_audit.json](core02_laliga_201516_audit.json) são evidências/contratos, não manuais duplicados. Não regenerar resumos com outra disponibilidade local para ocultar ausência de artefatos.

A consolidação remove a cronologia detalhada deste documento, preservada integralmente no [snapshot anterior](https://github.com/devMarcos12/ManagerAI/blob/f9315d91b82a8a3e3a91ecc1504d532c4248ade4/docs/CURRENT_VERSION.md). Não altera resultados históricos nem cria outra árvore de manuais por versão. Código/testes definem comportamento; histórico não autoriza instalações, exclusões ou publicação. Limpeza física exige manifesto exato aprovado e rollback, conforme [AGENTS.md](../AGENTS.md).
