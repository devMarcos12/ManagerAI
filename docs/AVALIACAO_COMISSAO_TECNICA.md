# Revisão das hipóteses pela comissão técnica

Este roteiro ainda não foi aplicado a especialistas. Sua existência não constitui validação esportiva. Revisar cada hipótese antes de usá-la em um planejamento real.

Identificação da revisão: hipótese, confronto, data de corte, versão das fórmulas, fingerprint dos dados, avaliador, data e função. Registrar respostas como sustentada / parcial / não sustentada / não avaliável, com justificativa e lances-fonte.

- A observação numérica confere com as métricas, jogos e denominadores citados no JSON?
- Há pelo menos cinco jogos calculáveis em cada métrica da hipótese e nas métricas centrais das duas equipes? A diferença de adversários e períodos limita sua aplicação?
- O texto distingue observação, interpretação e ação a testar? xG, pressão e blocos de posse foram interpretados corretamente?
- A amostra de vídeo confirma o tipo de entrada/zona de chute que motivou a hipótese? Quais IDs e situações concretas foram revisados?
- A ação proposta é plausível para treino? Que condição precisa existir para que seja testada? O registro histórico de atletas não comprova disponibilidade no alvo.
- Que espaços ou alternativas o ajuste pode oferecer ao adversário? Há um risco adicional não descrito?
- Qual comportamento observável será avaliado no treino (por exemplo, recepção no terço de ataque e cobertura do receptor)? Definir a medição antes do teste, sem escolher apenas exemplos favoráveis.
- A sugestão ajudou a decidir quais situações revisar? O técnico a usaria, adaptaria ou descartaria? Por quê?
- A linguagem foi compreensível sem ler fórmulas? Que expressão gerou dúvida?
- A revisão indicou limites que deveriam impedir a emissão ou exigir evidência adicional?

Registrar separadamente correção factual, rastreabilidade, compreensão, plausibilidade e utilidade. Não converter opinião favorável em acurácia de recomendação nem em prova de eficácia causal. Para estudar melhora de desempenho, será necessário desenho de avaliação próprio, baseline e controle dos contextos.

## Antes de considerar aprendizado de máquina

Definir variável-alvo, processo de rotulagem, avaliadores e concordância, quantidade de exemplos independentes e custo da coleta. Resultado de partida não é rótulo de estratégia ideal. Comparar qualquer modelo com o baseline determinístico, usar divisão temporal sem vazamento e selecionar métricas adequadas ao alvo. Só considerar fine-tuning após demonstrar dados/rótulos e melhora mensurável; não há experimento treinado nesta entrega.
