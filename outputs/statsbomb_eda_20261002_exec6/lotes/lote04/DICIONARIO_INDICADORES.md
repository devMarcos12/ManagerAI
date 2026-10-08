# Dicionário de indicadores

| Indicador | Fórmula/filtros | Unidade/denominador | Pergunta e limitação |
|---|---|---|---|
| Acerto de passe | `Pass` sem `pass.outcome` / Pass | % de passes tentados | segurança de circulação; outcome ausente segue convenção StatsBomb |
| Entradas no terço final | passe/condução inicia x<80 e termina x≥80 | por 90 observado | como progride; limiar é definição configurável deste estudo |
| Entradas na área | início fora; fim x≥102 e y 18–62 | por 90 | chegada à área; não mede perigo sozinho |
| xG e xG/chute | soma/média de `shot.statsbomb_xg` | por jogo / por chute | qualidade de chances; somente chutes com campo disponível |
| Pressures | eventos `Pressure` | por 90 | onde a equipe tenta pressionar; não mede sucesso isoladamente |
| Recuperações/interceptações | `Ball Recovery` / `Interception` | por 90 | ações distintas; sem chamar toda troca de posse de recuperação |
| Passe sob pressão | acerto condicionado a `under_pressure=True` | % / passes elegíveis | resistência à pressão; booleano ausente não é false globalmente |
| Corredores | ações localizadas em y 0–26,7; 26,7–53,3; 53,3–80 | % ações localizadas | ocupação relativa; não é orientação espelhada |
