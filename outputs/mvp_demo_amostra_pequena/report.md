# Relatório histórico de apoio pré-jogo

**Manchester City × Arsenal — Premier League 2015/2016**

Corte: 2016-05-08T17:00:00.000. Somente datas anteriores; o dia do corte é excluído.
Amostra: 2 jogos da equipe e 2 do adversário.

## Período observado

- Manchester City: 2016-04-23 a 2016-05-01; evidência insuficiente.
- Arsenal: 2016-04-24 a 2016-04-30; evidência insuficiente.

## Indicadores comparáveis

Taxas e proporções usam denominadores agregados; n indica jogos com métrica calculável.

| Indicador | Unidade | Equipe | n | Adversário | n |
|---|---|---:|---:|---:|---:|
| xG a favor | xG/jogo | 1,87 | 2 | 1,08 | 2 |
| xG contra | xG/jogo | 2,03 | 2 | 0,66 | 2 |
| Finalizações a favor | eventos/jogo | 8,50 | 2 | 17,00 | 2 |
| Finalizações contra | eventos/jogo | 14,50 | 2 | 12,00 | 2 |
| xG por chute | xG/chute | 0,22 | 2 | 0,06 | 2 |
| Acerto de passe | % | 83,36 | 2 | 82,90 | 2 |
| Acerto com pressão marcada | % | 74,87 | 2 | 71,61 | 2 |
| Acerto com ausência explícita de pressão | % | não disponível | 0 | não disponível | 0 |
| Acerto com pressão não marcada | % | 85,03 | 2 | 84,27 | 2 |
| Entradas no terço final por passe completo/condução | eventos/90 | 46,81 | 2 | 66,81 | 2 |
| Tentativas de entrada no terço final | eventos/90 | 60,39 | 2 | 86,90 | 2 |
| Entradas na área por passe completo/condução | eventos/90 | 15,92 | 2 | 26,16 | 2 |
| Eventos de pressão | eventos/90 | 150,27 | 2 | 125,68 | 2 |
| Pressões no terço ofensivo | % | 17,76 | 2 | 23,79 | 2 |
| Pressure com contrapressão marcada | eventos/90 | 36,51 | 2 | 36,44 | 2 |
| Eventos de recuperação | eventos/90 | 50,09 | 2 | 52,80 | 2 |
| Eventos de interceptação | eventos/90 | 11,23 | 2 | 12,61 | 2 |
| Duelos do tipo Tackle | eventos/90 | 19,19 | 2 | 12,61 | 2 |
| Ações localizadas em y menor que 80/3 | % | 32,83 | 2 | 35,77 | 2 |
| Ações localizadas no corredor central | % | 30,97 | 2 | 36,91 | 2 |
| Ações localizadas em y maior ou igual a 160/3 | % | 36,20 | 2 | 27,32 | 2 |

## Achados observáveis

- Comparação descritiva: xg a favor. Equipe: 1,87; adversário: 1,08 xG/jogo.
  Evidências: team_profile.metrics.xg_for, opponent_profile.metrics.xg_for.
- Comparação descritiva: xg contra. Equipe: 2,03; adversário: 0,66 xG/jogo.
  Evidências: team_profile.metrics.xg_against, opponent_profile.metrics.xg_against.
- Comparação descritiva: entradas no terço final por passe completo/condução. Equipe: 46,81; adversário: 66,81 eventos/90.
  Evidências: team_profile.metrics.final_third_entries, opponent_profile.metrics.final_third_entries.
- Comparação descritiva: eventos de pressão. Equipe: 150,27; adversário: 125,68 eventos/90.
  Evidências: team_profile.metrics.pressures, opponent_profile.metrics.pressures.

Diferenças observadas não demonstram superioridade, vulnerabilidade causal ou eficácia de uma estratégia.

## Hipóteses condicionais para investigação

Hipóteses não emitidas: amostra ou evidência insuficiente para as regras.
## Formação e escalação

Não suportado pelos dados atuais.

## Contexto informado pelo treinador

Mando declarado: desconhecido. Contexto declarado: regular.
Objetivo declarado: equilibrado.
Indisponíveis declarados (IDs): nenhum informado

Notas declaradas (texto do treinador, não verificado):

> Nenhuma nota informada.

## Lacunas e limites

- Adversário: amostra insuficiente (2 jogos; mínimo operacional 5).
- Adversário: locations_missing=41; consultar metodologia e dicionário de dados.
- Adversário: pass_accuracy_explicit_no_pressure calculável em 0/2 jogos.
- Ausência de marcação under_pressure é mantida separada de False explícito.
- Equipe: amostra insuficiente (2 jogos; mínimo operacional 5).
- Equipe: locations_missing=38; consultar metodologia e dicionário de dados.
- Equipe: pass_accuracy_explicit_no_pressure calculável em 0/2 jogos.
- Eventos não equivalem a tracking; a análise não usa dados 360 nem posicionamento integral sem bola.
- Formação e escalação: não suportado pelos dados atuais; formações registradas não comprovam adequação tática ou disponibilidade.
- Nenhuma hipótese emitida: amostra ou evidências não satisfazem as regras documentadas.
- Não há inferência de lesões, suspensões, rivalidade, importância competitiva ou mando real.
- Orientação preservada como registrada; corredores usam intervalos de y, sem inferir esquerda/direita tática.

## Metodologia e rastreabilidade

- Determinístico e descritivo; sem treinamento ou inferência causal.
- Somente datas anteriores ao corte; mesmo dia excluído conservadoramente. Nunca lê eventos ou escalações do alvo.
- Soma do maior timestamp + duration em cada período 1 e 2, em minutos; proxy de exposição observada, inclui acréscimos.
- Médias por jogo para contagens/xG; taxas por 90 e proporções agregadas por soma dos numeradores/denominadores. Mediana e DP entre jogos válidos.
- Plano StatsBomb 120×80, não metros. Coordenadas inválidas excluídas só dos cálculos espaciais.
- Menos de 5 jogos: insuficiente. A partir de 5: evidência limitada, sem confiança probabilística.
- Contexto e notas são declarações do treinador, não fatos verificados nem fatores causais.
- Template determinístico em português; nenhuma chamada a LLM.
- Fonte: StatsBomb Open Data; consultar README e LICENSE.pdf do conjunto local.

Versão das fórmulas: 1.0.0; regras: 1.0.0.
Fingerprint SHA-256 dos arquivos efetivamente lidos: `9604b216c34837427071d88ded59d65130bbbde226b4c7dde1165231351113d6`.
IDs das partidas, valores individuais, medianas, desvios-padrão, numeradores, denominadores e hashes das fontes estão em report.json.
