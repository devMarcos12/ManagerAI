# Contrato técnico V3 e definições

A API anterior `analyze(root, request)` e a CLI sem `--v3` continuam emitindo
`schema_version: 1.0.0`. A extensão opt-in retorna `AnalysisReportV3`, subclasse de
`AnalysisReport`, com **schema 1.1.0**. Todos os campos anteriores mantêm valores,
nomes e semântica; muda somente schema_version e acrescenta-se `tactical_v3`.
O JSON City original continua byte a byte idêntico sem a extensão. Nenhuma alteração
nas fórmulas ou regras 1.0.0 foi necessária. `software_version: 0.1.0` é preservado
nos campos legados; a versão das fórmulas/regras da extensão é **3.0.0**.

V3 disponível para recortes auditados **(2,27)** e **(11,90)**. Outros recortes
mantêm a análise anterior; a extensão rejeita seu uso antes de auditar campos e
orientação. Presença de arquivos no catálogo não implica validação semântica.

## Estrutura aditiva

`tactical_v3` contém:

- `formula_version`, `rules_version`: 3.0.0.
- `team_profile`, `opponent_profile`: team_id, team_name, match_ids, period_start,
  period_end, metrics, shots, quality, sequences, sequence_metrics, historical.
- `metric_definitions`: catálogo das 26 métricas abaixo, unidade, família e agregação.
- `hypotheses`: rule_id, title, observation, action, condition, evidence_metrics,
  preconditions, risks, limitations, confidence_level. Referências resolvem caminhos
  reais como `tactical_v3.opponent_profile.metrics.final_third_pass_entries`.
- `methodology`: políticas, mínimo operacional, fontes efetivamente lidas, SHA-256,
  fingerprint e limites. As releituras V3 devem coincidir com hashes do núcleo;
  mudança de conteúdo/cobertura entre as fases causa erro, sem relatório misturado.

Cada objeto em `metrics` e `sequence_metrics` segue `MetricEvidence`: metric_id,
value, unit, sample_size, match_ids, numerator, denominator, median,
standard_deviation, per_match, formula_version. `per_match` identifica partida,
data, valor, numerador e denominador. Nulos são JSON null, sem NaN/Infinity.
Uma observação não recebe desvio-padrão amostral. n é número de jogos **calculáveis
na métrica**, não todos os jogos solicitados.

Taxas por 90 = 90 × soma(contagens válidas) / soma(exposição válida). Proporções =
100 × soma(numeradores válidos) / soma(denominadores válidos). Médias xG por jogo =
soma(xG válido) / quantidade de jogos válidos. Mediana/desvio são entre valores
por partida, não estimativas de significância. Somente períodos 1 e 2.
A exposição é a mesma do núcleo, incluindo acréscimos; não é tempo de bola em jogo.

Geometria inválida em passe completo invalida métricas dependentes de passes
naquela partida, mantendo conduções válidas; falha em condução é simétrica.
Faixas de entradas dependem dos dois tipos. Localização inválida em chute invalida
métricas espaciais de chutes; xG ausente invalida somas/média xG, mantendo contagem
localizada. Pressão sem localização invalida suas métricas espaciais. Denominador
zero produz null. Ausência de uma categoria em fluxo íntegro pode ser contagem
zero; fluxo vazio/sem eventos da equipe é indisponível. Regras detalhadas e testes
estão em v3_features.py e test_v3_features.py.

`shots` conserva cada chute com posição válida, ID, match_id, team_id, period, x,
y e xg nullable; permite inspecionar o mapa sem reler JSONs brutos.

## Catálogo das três famílias prioritárias

Plano StatsBomb 120×80, sem chamar unidades de metros. Meta de referência (120,40).
A auditoria sustenta direção x crescente nos dois tempos dos recortes validados;
não há espelhamento automático. Faixas y não são esquerda/direita tática.

| ID | Nome | Unidade | Família | Definição |
|---|---|---|---|---|
| progressive_passes | Progressões por passe completo | eventos/90 | progression | Passe completo com início/fim válidos e redução de pelo menos 10 unidades na distância euclidiana à meta registrada (120,40); unidades StatsBomb, não metros. |
| final_third_pass_entries | Avanços ao terço de ataque por passe completo | eventos/90 | progression | Passe completo: início x<80 e destino x>=80, com coordenadas válidas. |
| box_pass_entries | Entradas na área por passe completo | eventos/90 | progression | Passe completo: início fora da área e destino em x>=102, 18<=y<=62. |
| progressive_carries | Progressões por condução | eventos/90 | progression | Condução com início/fim válidos e redução de pelo menos 10 unidades na distância euclidiana à meta registrada (120,40); unidades StatsBomb, não metros. |
| final_third_carry_entries | Avanços ao terço de ataque por condução | eventos/90 | progression | Condução: início x<80 e destino x>=80, com coordenadas válidas. |
| box_carry_entries | Entradas na área por condução | eventos/90 | progression | Condução: início fora da área e destino em x>=102, 18<=y<=62. |
| entry_lane_low_share | Avanços ao terço de ataque pela faixa de y baixo | % | progression | Proporção dos destinos dos avanços ao terço de ataque por passe completo/condução. Faixas: y<80/3, 80/3<=y<160/3, y>=160/3; sem significado de esquerda/direita. |
| pressure_lane_low_share | Tentativas de pressão na faixa de y baixo | % | pressure | Proporção das localizações de Pressure pelas faixas y<80/3, 80/3<=y<160/3, y>=160/3. Não mede sucesso nem posicionamento contínuo. |
| entry_lane_central_share | Avanços ao terço de ataque pela faixa central | % | progression | Proporção dos destinos dos avanços ao terço de ataque por passe completo/condução. Faixas: y<80/3, 80/3<=y<160/3, y>=160/3; sem significado de esquerda/direita. |
| pressure_lane_central_share | Tentativas de pressão na faixa central | % | pressure | Proporção das localizações de Pressure pelas faixas y<80/3, 80/3<=y<160/3, y>=160/3. Não mede sucesso nem posicionamento contínuo. |
| entry_lane_high_share | Avanços ao terço de ataque pela faixa de y alto | % | progression | Proporção dos destinos dos avanços ao terço de ataque por passe completo/condução. Faixas: y<80/3, 80/3<=y<160/3, y>=160/3; sem significado de esquerda/direita. |
| pressure_lane_high_share | Tentativas de pressão na faixa de y alto | % | pressure | Proporção das localizações de Pressure pelas faixas y<80/3, 80/3<=y<160/3, y>=160/3. Não mede sucesso nem posicionamento contínuo. |
| shots_box_share | Finalizações dentro da área | % | shots | Proporção de finalizações localizadas na zona; área x>=102, 18<=y<=62. |
| xg_box | Gols esperados em finalizações dentro da área | xG/jogo | shots | Soma de xG válido dos chutes na zona por partida; lacuna espacial ou de xG invalida a soma. |
| shots_outside_share | Finalizações fora da área | % | shots | Proporção de finalizações localizadas na zona; área x>=102, 18<=y<=62. |
| xg_outside | Gols esperados em finalizações fora da área | xG/jogo | shots | Soma de xG válido dos chutes na zona por partida; lacuna espacial ou de xG invalida a soma. |
| xg_per_located_shot | Qualidade média das finalizações localizadas | xG/chute | shots | Soma de xG / chutes localizados; exige localização e xG válidos em todos os chutes da partida. |
| pressures_low_third_share | Tentativas de pressão no terço de origem | % | pressure | Proporção das localizações de Pressure pelos intervalos x<40, 40<=x<80 e x>=80. A tentativa registrada não comprova êxito. |
| pressures_low_third | Tentativas de pressão no terço de origem por 90 | eventos/90 | pressure | Contagem de Pressure localizado no intervalo espacial por exposição observada de 90 minutos. |
| pressures_middle_third_share | Tentativas de pressão no terço intermediário | % | pressure | Proporção das localizações de Pressure pelos intervalos x<40, 40<=x<80 e x>=80. A tentativa registrada não comprova êxito. |
| pressures_middle_third | Tentativas de pressão no terço intermediário por 90 | eventos/90 | pressure | Contagem de Pressure localizado no intervalo espacial por exposição observada de 90 minutos. |
| pressures_high_third_share | Tentativas de pressão no terço de ataque | % | pressure | Proporção das localizações de Pressure pelos intervalos x<40, 40<=x<80 e x>=80. A tentativa registrada não comprova êxito. |
| pressures_high_third | Tentativas de pressão no terço de ataque por 90 | eventos/90 | pressure | Contagem de Pressure localizado no intervalo espacial por exposição observada de 90 minutos. |
| recoveries_recorded | Recuperações registradas | eventos/90 | pressure | Eventos Ball Recovery, sem inferir posse consolidada. |
| recoveries_explicit_failure | Recuperações com falha explícita | eventos/90 | pressure | Ball Recovery com recovery_failure=True. |
| recoveries_explicit_nonfailure | Recuperações sem falha explicitamente marcada | eventos/90 | pressure | Ball Recovery com recovery_failure=False; ausência da marcação não equivale a False. |

## Sequências e histórico exploratório

`sequences`: resultados por partida com valid_blocks, entry_blocks, shot_blocks,
entry_block_share, shot_block_share, blocks, quality, limitations. Os blocos são
contíguos por (period, possession, possession_team.id), ordenados por index.
Não unir um ID de posse que reapareça. Só Pass completo/Carry/Shot do titular
alimentam o denominador; pressão rival não é ação ofensiva do titular. Evidências
associam até três ações anteriores íntegras, interrompendo passes incompletos e
ações próprias que rompem o encadeamento. Não mede todas as posses reais, tempo de
posse, eficácia, contra-ataque ou causalidade.

`sequence_metrics`: média de blocos observados/jogo (`observed_blocks`), proporção
de blocos com entrada no terço ou área (`entry_block_share`), proporção com chute
(`shot_block_share`). Erros de contexto, relógio ou geometria tornam os totais do
jogo null; blocos íntegros permanecem para inspeção. n específico exclui esses
jogos somente desta família. Detalhes no docstring de v3_sequences.py.

`historical`: players em ordem alfabética, associações verificadas na escalação da
mesma equipe e partida, contagens de Pass/Carry/Shot/Pressure, total de xG e IDs
fontes. Denominador individual = jogos com ao menos uma ação selecionada registrada;
sem estimar minutos ou ranking. xG ausente em qualquer chute atribuído torna seu
acumulado null. Disponibilidade é sempre desconhecida. Roster ausente/associação
inválida exclui ações sem comprovação, com qualidade explícita.

Formações iniciais usam exclusivamente um Starting XI por jogo. Frequência = jogos
na formação / jogos com formação inicial calculável. Tactical Shift aparece como
mudança separada, nunca entra no denominador inicial nem comprova duração ou
adequação. match_dates permite períodos rastreáveis; IDs ficam no JSON.

## Novas hipóteses condicionais

Mínimo operacional padrão cinco, parametrizável no helper de regras. A aplicação
usa cinco e exige também suficiência central V2.2 nas duas equipes. Toda métrica
citada deve ter valor finito, denominador positivo e n suficiente. Os limiares
abaixo são heurísticos operacionais, sem calibração ou eficácia demonstrada.

- **V3_ENTRADAS_PASSE**: ao menos 60% das entradas do adversário no terço por passe
  entre passe/condução. As duas taxas devem usar partidas e exposições idênticas.
  Cita também o indicador próprio de entradas por passe; propõe investigar proteção
  de recepções, com risco de abrir conduções e condição de vídeo/treino.
- **V3_CHUTES_AREA**: ao menos 60% dos chutes localizados adversários dentro da área;
  exige xG da zona e a proporção própria calculáveis. Propõe investigar proteção
  dos espaços antes do chute, sem inferir falha causal ou eficácia defensiva.

Campos manuais não alteram valores, critérios ou ordem editorial nesta entrega.
Sem fine-tuning, LLM, odds, probabilidade de vitória ou recomendação de escalação.

Fonte: StatsBomb Open Data local. [Viabilidade](V3_DATA_FEASIBILITY.md),
[conferência independente](V3_METRICS_CHECK.md) e [tutorial](TUTORIAL_V3.md).
