# Relatório histórico de apoio pré-jogo

**Manchester City × Arsenal — Premier League 2015/2016**

Corte: 2015-08-08. Somente datas anteriores; o dia do corte é excluído.
Amostra: 0 jogos da equipe e 0 do adversário.

## Período observado

- Manchester City: sem histórico a sem histórico; evidência insuficiente.
- Arsenal: sem histórico a sem histórico; evidência insuficiente.

## Indicadores comparáveis

Taxas e proporções usam denominadores agregados; n indica jogos com métrica calculável.

| Indicador | Unidade | Equipe | n | Adversário | n |
|---|---|---:|---:|---:|---:|
| xG a favor | xG/jogo | não disponível | 0 | não disponível | 0 |
| xG contra | xG/jogo | não disponível | 0 | não disponível | 0 |
| Finalizações a favor | eventos/jogo | não disponível | 0 | não disponível | 0 |
| Finalizações contra | eventos/jogo | não disponível | 0 | não disponível | 0 |
| xG por chute | xG/chute | não disponível | 0 | não disponível | 0 |
| Acerto de passe | % | não disponível | 0 | não disponível | 0 |
| Acerto com pressão marcada | % | não disponível | 0 | não disponível | 0 |
| Acerto com ausência explícita de pressão | % | não disponível | 0 | não disponível | 0 |
| Acerto com pressão não marcada | % | não disponível | 0 | não disponível | 0 |
| Entradas no terço final por passe completo/condução | eventos/90 | não disponível | 0 | não disponível | 0 |
| Tentativas de entrada no terço final | eventos/90 | não disponível | 0 | não disponível | 0 |
| Entradas na área por passe completo/condução | eventos/90 | não disponível | 0 | não disponível | 0 |
| Eventos de pressão | eventos/90 | não disponível | 0 | não disponível | 0 |
| Pressões no terço ofensivo | % | não disponível | 0 | não disponível | 0 |
| Pressure com contrapressão marcada | eventos/90 | não disponível | 0 | não disponível | 0 |
| Eventos de recuperação | eventos/90 | não disponível | 0 | não disponível | 0 |
| Eventos de interceptação | eventos/90 | não disponível | 0 | não disponível | 0 |
| Duelos do tipo Tackle | eventos/90 | não disponível | 0 | não disponível | 0 |
| Ações localizadas em y menor que 80/3 | % | não disponível | 0 | não disponível | 0 |
| Ações localizadas no corredor central | % | não disponível | 0 | não disponível | 0 |
| Ações localizadas em y maior ou igual a 160/3 | % | não disponível | 0 | não disponível | 0 |

## Achados observáveis

Não há evidência comparável suficiente para emitir achados.

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

- Adversário: amostra insuficiente (0 jogos; mínimo operacional 5).
- Ausência de marcação under_pressure é mantida separada de False explícito.
- Equipe: amostra insuficiente (0 jogos; mínimo operacional 5).
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
Fingerprint SHA-256 dos arquivos efetivamente lidos: `5cfcf0cf901ad76dcebe2121e9804d98d96279e3924392c45238b0bf9d9bfa62`.
IDs das partidas, valores individuais, medianas, desvios-padrão, numeradores, denominadores e hashes das fontes estão em report.json.
