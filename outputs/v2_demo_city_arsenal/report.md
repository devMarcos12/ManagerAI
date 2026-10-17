# Preparação pré-jogo — ManagerAI

## Visão geral do confronto

Manchester City × Arsenal — Premier League 2015/2016.
Referência histórica: 08/05/2016. O dia da referência fica fora da análise.
Manchester City: 10 jogos, de 02/03/2016 a 01/05/2016.
Arsenal: 10 jogos, de 28/02/2016 a 30/04/2016.
Este relatório usa dados históricos locais; não descreve os elencos ou a situação atual dos clubes.

## Resumo para a comissão técnica

- Finalizações por jogo: 13,30 por jogo para Manchester City (10 jogos) e 15,30 por jogo para Arsenal (10 jogos).
- Qualidade estimada das chances criadas: 1,58 gols esperados por jogo para Manchester City (10 jogos) e 1,50 gols esperados por jogo para Arsenal (10 jogos).
- Qualidade estimada das chances permitidas: 1,03 gols esperados por jogo para Manchester City (10 jogos) e 0,75 gols esperados por jogo para Arsenal (10 jogos).
- Passes certos: 81,93 % para Manchester City (10 jogos) e 83,79 % para Arsenal (10 jogos).
- Entradas no terço de ataque: 59,90 por 90 min para Manchester City (10 jogos) e 63,54 por 90 min para Arsenal (10 jogos).

A evidência continua limitada: adversários e datas podem diferir entre as janelas. As diferenças não comprovam superioridade ou eficácia de um ajuste.
Há registros ausentes ou ocorrências de qualidade nas partidas analisadas. A disponibilidade de cada indicador e as ocorrências constam dos detalhes técnicos.

Gols esperados (xG) representam a soma dos valores esperados das finalizações. Não são uma contagem de chances, gols reais ou probabilidade de vencer.

## Comparação dos times

As taxas por 90 min consideram o tempo observado, incluindo acréscimos. Indisponível significa ausência de informação calculável, nunca zero.

| Indicador | Unidade | Manchester City | Arsenal | Jogos disponíveis (equipe / adversário) | Como ler |
|---|---|---:|---:|---|---|
| Finalizações por jogo | por jogo | 13,30 | 15,30 | 10 / 10 | Quantidade média de chutes registrados. |
| Qualidade estimada das chances criadas | gols esperados por jogo | 1,58 | 1,50 | 10 / 10 | Gols esperados (xG): soma dos valores esperados das finalizações. Não é quantidade de chances, gols reais ou probabilidade de vencer. |
| Finalizações permitidas por jogo | por jogo | 9,40 | 11,40 | 10 / 10 | Quantidade média de chutes dos adversários. |
| Qualidade estimada das chances permitidas | gols esperados por jogo | 1,03 | 0,75 | 10 / 10 | Valor esperado dos chutes adversários. Não representa os gols efetivamente sofridos. |
| Passes certos | % | 81,93 | 83,79 | 10 / 10 | Percentual de passes completos entre os passes tentados. |
| Entradas no terço de ataque | por 90 min | 59,90 | 63,54 | 10 / 10 | Passes completos ou conduções que levam a bola de antes do terço de ataque para dentro dele. |
| Entradas na área por passe ou condução | por 90 min | 19,43 | 22,52 | 10 / 10 | Passes completos ou conduções que levam a bola de fora para dentro da área. Não conta toda forma possível de entrada. |
| Ações de pressão registradas | por 90 min | 143,26 | 127,07 | 10 / 10 | Quantidade de ações registradas; maior volume não significa pressão mais eficaz. |

## O que merece atenção no adversário

- Arsenal — finalizações por jogo: 15,30 por jogo, em 10 jogos com informação disponível. O volume não basta para afirmar que um ataque é mais forte; confira a localização e o contexto dos chutes.
- Arsenal — qualidade estimada das chances criadas: 1,50 gols esperados por jogo, em 10 jogos com informação disponível. Esse valor descreve a qualidade estimada das finalizações, sem prever gols ou vitória no confronto.
- Arsenal — entradas no terço de ataque: 63,54 por 90 min, em 10 jogos com informação disponível. São avanços da bola por passe completo ou condução; a zona específica exige revisão em vídeo.
- Arsenal — ações de pressão registradas: 127,07 por 90 min, em 10 jogos com informação disponível. O número de ações não informa quantas pressões deram certo e não define sozinho um estilo de jogo.

## Possíveis ajustes para avaliar em treino ou vídeo

### Preparar a proteção das zonas de chegada

**O que foi observado:** Arsenal — entradas no terço de ataque: 63,54 por 90 min (10 jogos com informação disponível); Manchester City — entradas no terço de ataque: 59,90 por 90 min (10 jogos com informação disponível).

**Por que importa:** Essas ações registram avanços da bola até o terço de ataque; não mostram, sozinhas, o perigo de cada chegada.

**O que verificar ou testar:** Rever em vídeo como essas entradas acontecem e ensaiar coberturas em treino. A zona específica e a altura do bloco ainda precisam dessa verificação.

**Condição:** Há entradas observadas por passe completo/condução no histórico do adversário e comparação disponível com o próprio time.

**Antes de testar:**

- Revisar sequências em vídeo antes de escolher altura de bloco ou corredores prioritários.
- Confirmar em treino a capacidade de cobertura dos atletas disponíveis.

**Riscos:**

- Recuar o bloco pode conceder território e reduzir opções de saída.

**Limitações:**

- Sugestão exploratória: não foi demonstrado que esse ajuste melhora o desempenho.
- Histórico observado não garante repetição do comportamento no jogo-alvo.

### Rever a proteção dos espaços de finalização

**O que foi observado:** Arsenal — qualidade estimada das chances criadas: 1,50 gols esperados por jogo (10 jogos com informação disponível); Manchester City — qualidade estimada das chances permitidas: 1,03 gols esperados por jogo (10 jogos com informação disponível).

**Por que importa:** A qualidade estimada das finalizações complementa a contagem de chutes. A média não identifica onde está uma falha defensiva nem prevê gols no confronto.

**O que verificar ou testar:** Rever a localização e o contexto das finalizações nas partidas analisadas e testar a proteção desses espaços em treino, antes de escolher um ajuste defensivo.

**Condição:** O adversário criou chances com gols esperados positivos; há histórico de gols esperados permitidos do próprio time para comparação.

**Antes de testar:**

- Inspecionar localização e contexto dos chutes nas partidas-fonte; a média de gols esperados não identifica sozinha uma vulnerabilidade espacial.

**Riscos:**

- Priorizar a proteção da área pode aumentar a liberdade adversária em outras zonas.

**Limitações:**

- Sugestão exploratória: não foi demonstrado que esse ajuste melhora o desempenho.
- Histórico observado não garante repetição do comportamento no jogo-alvo.

## Informações declaradas pelo treinador

São um cenário de planejamento informado manualmente. Não alteram o cálculo nem os critérios das hipóteses nesta versão.

- Mando declarado: desconhecido.
- Contexto declarado: regular.
- Objetivo declarado: equilibrado.
- Jogadores indisponíveis declarados: 0; não há sugestão de substitutos.

Notas declaradas (texto do treinador, não verificado):

> Nenhuma nota informada.

## O que o sistema ainda não consegue recomendar

Formação ideal e escalação: não suportado pelos dados atuais. Não suportado pelos dados atuais significa uma limitação deliberada, não uma falha de execução.
Não são inferidos lesões, suspensões, disponibilidade presente, resultado do confronto ou eficácia comprovada de um ajuste.
As faixas espaciais não são chamadas automaticamente de esquerda ou direita: a orientação ainda precisa ser validada.

## Como conferir a análise

A apresentação vem do mesmo relatório calculado pela CLI. O relatório técnico em JSON preserva valores exatos, partidas, fórmulas e fontes. As hipóteses são exploratórias e exigem avaliação da comissão técnica.

Fonte: StatsBomb Open Data. Nenhum modelo foi treinado e nenhuma LLM foi utilizada.

## Apêndice técnico — indicadores e rastreabilidade

### Relatório histórico de apoio pré-jogo

**Manchester City × Arsenal — Premier League 2015/2016**

Corte: 2016-05-08T17:00:00.000. Somente datas anteriores; o dia do corte é excluído.
Amostra: 10 jogos da equipe e 10 do adversário.

#### Período observado

- Manchester City: 2016-03-02 a 2016-05-01; evidência limitada.
- Arsenal: 2016-02-28 a 2016-04-30; evidência limitada.

#### Indicadores comparáveis

Taxas e proporções usam denominadores agregados; n indica jogos com métrica calculável.

| Indicador | Unidade | Equipe | n | Adversário | n |
|---|---|---:|---:|---:|---:|
| xG a favor | xG/jogo | 1,58 | 10 | 1,50 | 10 |
| xG contra | xG/jogo | 1,03 | 10 | 0,75 | 10 |
| Finalizações a favor | eventos/jogo | 13,30 | 10 | 15,30 | 10 |
| Finalizações contra | eventos/jogo | 9,40 | 10 | 11,40 | 10 |
| xG por chute | xG/chute | 0,12 | 10 | 0,10 | 10 |
| Acerto de passe | % | 81,93 | 10 | 83,79 | 10 |
| Acerto com pressão marcada | % | 74,71 | 10 | 76,42 | 10 |
| Acerto com ausência explícita de pressão | % | não disponível | 0 | não disponível | 0 |
| Acerto com pressão não marcada | % | 83,45 | 10 | 84,90 | 10 |
| Entradas no terço final por passe completo/condução | eventos/90 | 59,90 | 10 | 63,54 | 10 |
| Tentativas de entrada no terço final | eventos/90 | 78,30 | 10 | 81,65 | 10 |
| Entradas na área por passe completo/condução | eventos/90 | 19,43 | 10 | 22,52 | 10 |
| Eventos de pressão | eventos/90 | 143,26 | 10 | 127,07 | 10 |
| Pressões no terço ofensivo | % | 22,54 | 10 | 23,04 | 10 |
| Pressure com contrapressão marcada | eventos/90 | 35,77 | 10 | 35,38 | 10 |
| Eventos de recuperação | eventos/90 | 51,82 | 10 | 52,84 | 10 |
| Eventos de interceptação | eventos/90 | 18,31 | 10 | 16,14 | 10 |
| Duelos do tipo Tackle | eventos/90 | 19,43 | 10 | 17,17 | 10 |
| Ações localizadas em y menor que 80/3 | % | 34,61 | 10 | 32,30 | 10 |
| Ações localizadas no corredor central | % | 29,63 | 10 | 33,26 | 10 |
| Ações localizadas em y maior ou igual a 160/3 | % | 35,76 | 10 | 34,44 | 10 |

#### Achados observáveis

- Comparação descritiva: xg a favor. Equipe: 1,58; adversário: 1,50 xG/jogo.
  Evidências: team_profile.metrics.xg_for, opponent_profile.metrics.xg_for.
- Comparação descritiva: xg contra. Equipe: 1,03; adversário: 0,75 xG/jogo.
  Evidências: team_profile.metrics.xg_against, opponent_profile.metrics.xg_against.
- Comparação descritiva: entradas no terço final por passe completo/condução. Equipe: 59,90; adversário: 63,54 eventos/90.
  Evidências: team_profile.metrics.final_third_entries, opponent_profile.metrics.final_third_entries.
- Comparação descritiva: eventos de pressão. Equipe: 143,26; adversário: 127,07 eventos/90.
  Evidências: team_profile.metrics.pressures, opponent_profile.metrics.pressures.

Diferenças observadas não demonstram superioridade, vulnerabilidade causal ou eficácia de uma estratégia.

#### Hipóteses condicionais para investigação

##### R01_PROGRESSAO

Investigar a proteção das zonas de chegada do adversário e ensaiar respostas às entradas no terço final.

Condição: Há entradas observadas por passe completo/condução no histórico do adversário e comparação disponível com o próprio time.
Evidências: opponent_profile.metrics.final_third_entries, team_profile.metrics.final_third_entries.
Qualidade da evidência: limitada.

Pré-condições:

- Revisar sequências em vídeo antes de escolher altura de bloco ou corredores prioritários.
- Confirmar em treino a capacidade de cobertura dos atletas disponíveis.

Riscos:

- Recuar o bloco pode conceder território e reduzir opções de saída.

Limitações:

- Regra exploratória sem validação causal ou de eficácia.
- Histórico observado não garante repetição do comportamento no jogo-alvo.

##### R03_CHANCES

Investigar a proteção da área e dos espaços de finalização antes de definir ajustes defensivos.

Condição: O adversário criou chances com xG positivo; há histórico de xG concedido do próprio time para comparação.
Evidências: opponent_profile.metrics.xg_for, team_profile.metrics.xg_against.
Qualidade da evidência: limitada.

Pré-condições:

- Inspecionar localização e contexto dos chutes nas partidas-fonte; a média de xG não identifica sozinha uma vulnerabilidade espacial.

Riscos:

- Priorizar a proteção da área pode aumentar a liberdade adversária em outras zonas.

Limitações:

- Regra exploratória sem validação causal ou de eficácia.
- Histórico observado não garante repetição do comportamento no jogo-alvo.

#### Formação e escalação

Não suportado pelos dados atuais.

#### Contexto informado pelo treinador

Mando declarado: desconhecido. Contexto declarado: regular.
Objetivo declarado: equilibrado.
Indisponíveis declarados (IDs): nenhum informado

Notas declaradas (texto do treinador, não verificado):

> Nenhuma nota informada.

#### Lacunas e limites

- Adversário: locations_missing=204; consultar metodologia e dicionário de dados.
- Adversário: pass_accuracy_explicit_no_pressure calculável em 0/10 jogos.
- Ausência de marcação under_pressure é mantida separada de False explícito.
- Equipe: locations_missing=195; consultar metodologia e dicionário de dados.
- Equipe: pass_accuracy_explicit_no_pressure calculável em 0/10 jogos.
- Eventos não equivalem a tracking; a análise não usa dados 360 nem posicionamento integral sem bola.
- Formação e escalação: não suportado pelos dados atuais; formações registradas não comprovam adequação tática ou disponibilidade.
- Não há inferência de lesões, suspensões, rivalidade, importância competitiva ou mando real.
- Orientação preservada como registrada; corredores usam intervalos de y, sem inferir esquerda/direita tática.

#### Metodologia e rastreabilidade

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
Fingerprint SHA-256 dos arquivos efetivamente lidos: `a35bcbeb3d42705618b1c4463f32ceb6383f19a73699ab6cd3662096db40c915`.
IDs das partidas, valores individuais, medianas, desvios-padrão, numeradores, denominadores e hashes das fontes estão em report.json.
