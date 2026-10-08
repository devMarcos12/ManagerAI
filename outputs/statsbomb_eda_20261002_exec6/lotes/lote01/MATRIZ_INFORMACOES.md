# Matriz para o futuro dataset pré-jogo

| Informação necessária | Campo/fonte | Tipo | Cobertura | Uso |
|---|---|---|---|---|
| Identidade/data/placar agendado | matches | direta | alta no recorte | chave temporal; placar final não entra pré-jogo |
| Fase | `competition_stage` | derivada/direta | quando preenchido | segmentação; não prova jogo decisivo |
| Mando formal | home/away em matches | direta | alta | contexto, distinto de mando real |
| Mando real/campo neutro | cadastro estádio/calendário verificável | externa | indisponível aqui | entrada do coach/integração |
| Clássico/rivalidade | cadastro externo verificável | externa | indisponível | nunca inferir pelo nome |
| Título/classificação/rebaixamento | tabela e regulamento datados | externa/derivada | indisponível | importância do jogo |
| Lesões/suspensões/disponibilidade | clube/coach/registro oficial | externa | indisponível | cenário de elenco |
| Perfil histórico até corte | eventos anteriores | derivada | depende da cobertura | indicadores pré-jogo |
| Eventos/xG/placar do alvo | eventos da partida-alvo | pós-jogo | só após apito | proibido como feature pré-jogo |
