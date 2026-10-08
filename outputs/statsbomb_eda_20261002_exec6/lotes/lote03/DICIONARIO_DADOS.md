# Dicionário de dados relevante

| Caminho JSON | Tipo | Aplicável a | Significado/uso tático | Tratamento |
|---|---|---|---|---|
| `id`, `index`, `period`, `timestamp` | string/inteiro | todos | chave e ordenação documentada | `index` preservado; eventos simultâneos não são eliminados |
| `team.id`, `player.id`, `possession`, `possession_team.id` | inteiro | quando aplicável | vínculos equipe/jogador/posse | IDs, nunca nomes, são chave |
| `location`, `pass.end_location`, `carry.end_location` | lista numérica | ações localizadas | plano 120×80 StatsBomb | ausente ≠ zero; unidades não são metros |
| `pass.outcome` | objeto/nulo | Pass | resultado; ausência representa passe completo | `pass_completed=True` somente em Pass sem outcome |
| `pass.length`, `height`, `cross`, `under_pressure` | número/objeto/booleano | Pass/ação | construção, altura/cruzamento/pressão sofrida | cobertura calculada no denominador aplicável |
| `shot.statsbomb_xg`, `shot.outcome`, `shot.type` | número/objeto | Shot | qualidade/contexto de finalização | xG avaliado apenas entre chutes |
| `pressure`, `ball_recovery` | objeto | Pressure/Recovery | ação defensiva da equipe | não confundir Pressure com `under_pressure` |
| `tactics.formation` | inteiro | Starting XI/Tactical Shift | formação registrada | não infere organização dinâmica |
| `freeze_frame`, `three-sixty[].freeze_frame`, `visible_area` | listas | chutes/360 | contexto espacial visível | não expande eventos; fora da visão ≠ ausente |

**Ausente**: chave não fornecida; **nulo**: chave presente sem valor; **não aplicável**: evento de outra categoria. Frequências mensuradas encontram-se nas tabelas de qualidade, filtradas ao tipo de evento aplicável.
