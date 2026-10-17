# Hipóteses condicionais — regras 1.0.0

O motor em `recommendation_engine.py` é determinístico e exploratório. Não foi
treinado, não otimiza probabilidade de vitória e não identifica uma tática ideal.
As regras propõem investigações e ensaios condicionais, com riscos e pré-condições.

Para emitir hipóteses, ambos os perfis precisam de ao menos cinco partidas. Cada
métrica citada precisa de valor disponível e cinco jogos elegíveis. Pode haver
zero, uma, duas ou três hipóteses: não são completadas artificialmente para cumprir
uma quantidade quando a evidência é insuficiente.

| Regra | Gatilho mensurável | Hipótese e limite |
|---|---|---|
| R01_PROGRESSAO | Entradas no terço final calculáveis para ambas as equipes e valor adversário >0 | Investigar proteção das zonas de chegada. Não afirma que o adversário seja superior ou que o bloco deva recuar |
| R02_PRESSAO_ALTA | ≥30% dos Pressure localizados do adversário no terço ofensivo e acerto do próprio time sob pressão calculável | Investigar rotas de saída e apoios. Não infere pressão bem-sucedida nem resistência comprovada |
| R03_CHANCES | xG favorável adversário >0 e xG concedido do próprio time calculável | Investigar proteção da área e dos espaços de finalização. A média não localiza uma vulnerabilidade |

O limiar de 30% é uma escolha operacional **não calibrada**. Não há pontuação
oculta, recomendação aprendida ou confiança probabilística. `confidence_level`
permanece `limitada` para hipóteses emitidas.

Cada hipótese contém `rule_id`, condição, caminhos das métricas no JSON, riscos,
pré-condições e limitações. As partidas e fórmulas podem ser recuperadas por esses
caminhos. As notas, objetivos e contexto do treinador são apresentados como
declarações manuais; não alteram as regras como se tivessem efeito causal validado.

Formações e escalações permanecem vazias, com justificativa explícita. Observação
anterior de um atleta não comprova disponibilidade no alvo. Não se usa a escalação
do alvo para reconstruir informação pré-jogo.
