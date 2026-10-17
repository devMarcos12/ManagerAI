# Entrega ManagerAI V2.2 e V3

Execução local em 11/10/2026. Marcos A e B implementados e validados em sequência.
Sem commits/push, serviços externos, LLM, fine-tuning ou alteração de dados brutos.

## Entregas

**V2.2:** prévia reativa por competição/temporada, equipes, corte e janela,
distinguindo calendário, seleção e arquivos presentes. Não abre eventos antes do
envio. Avisos de amostra pequena antes/depois, n e período por indicador, valores
válidos preservados como consulta descritiva, sem conclusões comparativas quando
qualquer métrica central tem valor ausente ou n<5. Português corrigido, xG explicado,
pressão sem alegação de êxito e contexto manual explicitamente sem efeito analítico.

**V3:** 26 indicadores em três famílias prioritárias: nove de progressão segmentada,
cinco de finalizações/xG espacial e doze de pressão/recuperações registradas. Além
deles, três agregados de sequências e exploração de atletas/formações históricas,
sem ranking, minutos presumidos, disponibilidade inferida ou escalação recomendada.
Hipóteses condicionais citam métricas, amostras, condição, pré-condições, risco e
limitações. Dois gráficos exportáveis e exibidos no Streamlit: mapa de chutes/xG
e entradas no terço de ataque por passe/condução.

A auditoria integral de campos e orientação cobre PL 2015/16 e La Liga 2020/21;
a extensão V3 é habilitada apenas nesses recortes. O catálogo anterior continua
disponível para outras temporadas, sem presumir que foram auditadas para a V3.

Código novo: coverage.py e v3_{features,sequences,history,schema,pipeline,rules,
presentation,plots}.py em src/managerai. Integrações: pipeline.py, cli.py,
report_renderer.py, streamlit_ui.py e presentation/{coach_report,terminology}.py.
Testes novos: test_{coverage,v22_presentation,v22_ui,v3_features,v3_sequences,
v3_history,v3_integration,v3_presentation,v3_rules,v3_ui}.py. Dois testes anteriores
de apresentação foram adaptados à nova abstenção por passes adversários ausentes;
a cobertura não foi enfraquecida. README, pyproject e requirements-v3.txt documentam
as dependências opcionais. O ambiente já possuía Streamlit 1.65.0/Matplotlib 3.11.2;
não foi necessário instalar pacotes nesta execução.

## Compatibilidade e rastreabilidade

API/CLI padrão preservam schema 1.0.0 e os resultados originais. `include_v3=True`
ou `--v3` acrescentam tactical_v3 e schema 1.1.0, com fórmulas/regras adicionais
3.0.0. Campos anteriores e seu significado não mudam. O software_version legado
0.1.0 permanece para compatibilidade; versões da extensão estão no payload.

Relatório City V2.2 idêntico byte a byte ao JSON V1: SHA-256
`424389e2af0afee96eff3d5a7ef79d74f914f12f0965a052d361fe657fd56b08`.
Testes também comparam todos os campos antigos da V3 e os resultados de CLI/UI/API.
Hashes detectam mudança entre leitura do núcleo e releitura V3; alteração de cobertura
entre fases interrompe a análise. Os mesmos relatórios demonstrativos foram
recalculados e seus JSONs coincidiram exatamente.

A conferência de preservação verificou tamanho e mtime_ns dos **9.108 arquivos
originais** de open-data/data e outputs monitorados no início: zero alterados ou
ausentes. Esta checagem de integridade de arquivos é por metadados; os JSONs usados
nos relatórios/auditoria também possuem hashes de conteúdo. Outputs antigos não
foram sobrescritos. HEAD inicial/final e status ficam no diretório de validação;
nenhum comando de commit, push, reset, clean, PR ou publicação foi executado.

## Exemplos reais gerados

| Cenário | Amostra equipe/adversário | Hipóteses anteriores | Novas hipóteses | Jogos calculáveis de sequências | Participantes históricos |
|---|---|---|---|---|---|
| City × Arsenal, 08/05/2016 | 10/10 | 2 | 2 | 9/7 | 23/21 |
| Real Madrid × Barcelona, 10/04/2021 | 1/10 | 0 | 0 | 1/7 | 14/21 |

- [City: relatório revisado](../outputs/v3_demo_city_arsenal/report.md),
  [JSON](../outputs/v3_demo_city_arsenal/report.json),
  [mapa de chutes](../outputs/v3_demo_city_arsenal/shot_map.png),
  [progressão](../outputs/v3_demo_city_arsenal/progression_entries.png).
- [Real × Barcelona: relatório revisado](../outputs/v3_demo_real_madrid_barcelona/report.md),
  [JSON](../outputs/v3_demo_real_madrid_barcelona/report.json),
  [mapa](../outputs/v3_demo_real_madrid_barcelona/shot_map.png),
  [progressão](../outputs/v3_demo_real_madrid_barcelona/progression_entries.png).
- V2.2 sem extensão: outputs/v22_city_arsenal e outputs/v22_real_madrid_barcelona.

City usa 02/03–01/05/2016; Arsenal 28/02–30/04/2016. Real tem apenas 24/10/2020;
Barcelona 31/01–05/04/2021. O desequilíbrio é cobertura real do snapshot, não erro
aritmético. Não houve junção com outras temporadas nem compensação com futuros.

A primeira geração V3 em outputs/v3_city_arsenal e outputs/v3_real_madrid_barcelona
foi preservada como registro de validação. A revisão visual encontrou uma barra
cortada no gráfico de progressão; a escala foi corrigida e ganhou teste específico.
Os diretórios **v3_demo_...** acima são as versões gráficas revisadas. Imagens PNG
foram inspecionadas; não foi realizada navegação manual completa em navegador.

## Testes executados e resultados

| Verificação | Resultado | Evidência |
|---|---|---|
| Baseline inicial | 48 aprovados, 7,225 s | v22_baseline.log |
| Gate Marco A antes de implementar B | 64 aprovados, 9,640 s | v22_tests.log |
| Interface A1 adicional | 14 execuções aprovadas, 5,755 s; inclui reutilizações | v22_ui.log |
| Suíte final com dependências e dados reais | **135 aprovados, zero falhas, 46,988 s** | complete_tests.log |
| Sem site-packages (`python3 -S`) | **117 aprovados; 18 pulados; zero falhas**, 21,912 s | stdlib_tests.log |
| Recalculo independente de oito métricas em dois JSONs | **16 conferências aprovadas**, tolerância 1e-12 | independent_metrics.json |
| Dependências instaladas | pip check sem dependências quebradas | dependency_check.txt |
| Reprodução dos relatórios e preservação | JSONs iguais; 9.108 arquivos preservados | preservation_and_reports.json |

Evidências em [outputs/v22_v3_validation](../outputs/v22_v3_validation/).
A suíte cobre geometria e fronteiras, associação equipe/jogador, agregação/denominador,
campos ausentes, fluxos vazios, n=0/1, blocos contíguos, posse reaparecendo, relógios
inválidos, limiares de hipóteses e n específico por evidência. Corromper eventos e
escalações sintéticos de alvo/futuro mantém JSON V3 exatamente igual; nenhum JSON
real foi corrompido. Mudanças manuais de contexto/objetivo mantêm indicadores e regras.

AppTest verificou seleção por nomes, prévia sem ler eventos, janela reativa,
abstenção, downloads, limpeza de resultado e duas imagens efetivamente renderizadas,
incluindo City e Real × Barça reais. Trocar para temporada não auditada desabilita
e desmarca V3. Testes de figuras verificam exportação PNG, escala comum sem cortar
barras, n=1 singular e xG ausente. Avisos `missing ScriptRunContext` de AppTest são
mensagens do modo de teste, sem falha de execução.

## Executar e testar

Na raiz do projeto:

```bash
MPLCONFIGDIR=/tmp/managerai-mpl venv/bin/python -m streamlit run streamlit_app.py
```

Abra http://localhost:8501 e marque **Incluir análise tática por eventos (V3)**.
A UI anterior segue como padrão. Para outra execução City em um diretório novo:

```bash
MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m managerai analyze --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 --target-match-id 3754314 --window 10 --v3 --output-dir outputs/minha_nova_execucao_city_v3
MANAGERAI_RUN_LOCAL_TESTS=1 MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m unittest discover -s tests -v
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src python3 -S -B -m unittest discover -s tests -v
venv/bin/python -m pip check
```

O diretório de saída precisa não existir. A CLI recusa sobrescrever arquivos ou
escrever dentro de open-data/data. No stdout, hypotheses conta regras anteriores;
v3_hypotheses conta novas, sem misturar os dois contratos. Tutorial passo a passo:
[TUTORIAL_V3.md](TUTORIAL_V3.md). Núcleo anterior: [TUTORIAL_TESTES.md](TUTORIAL_TESTES.md).

## Limites e próximo avanço

Amostra mínima cinco é regra operacional, não significância ou confiança calibrada.
Diferenças de adversários, períodos e contexto limitam comparação. PL não tem 360;
La Liga 2020/21 tem arquivos, mas seu conteúdo não foi validado nem consumido.
Não há tracking, ocupação contínua sem bola ou orientação esquerda/direita tática
certificada. A V3 descreve pressão e recuperações separadamente: recuperação após
pressão, eficácia de pressão e contra-ataques efetivos permanecem não inferidos.

IDs de posse podem retroceder; blocos não são agrupados globalmente pelo número.
Relógios decrescentes excluem somente sequências desses jogos: City 3754124;
Arsenal 3754239, 3754118, 3754009; Barcelona 3773625, 3773597, 3773474.
Isso reduz n dessa família sem mudar os indicadores V2 ou outras famílias V3.
Formações e participantes são históricos; não demonstram adequação, habilidade,
minutagem ou disponibilidade. Sem avaliações esportivas feitas por especialistas,
as hipóteses não têm eficácia demonstrada.

Próximos passos:

1. Aplicar o [checklist da comissão técnica](AVALIACAO_COMISSAO_TECNICA.md), revisar
   lances, compreensão e utilidade. Fazer avaliação manual de navegação/acessibilidade.
2. Auditar novos recortes antes de habilitar V3. Estudar integração de temporadas
   com envelhecimento da evidência e mudanças de elenco/comissão; nada automático.
3. Validar regras para associações pressão→recuperação e tempos de transição, com
   atribuição espacial/posse e interrupções explícitas. Ampliar evidência em vídeo.
4. Considerar personalização editorial por objetivo declarado, sem alterar métricas
   ou afirmar causalidade. Hoje o cenário não altera nem a ordem das hipóteses.
5. Otimizar cache/releituras e tamanho do JSON exploratório (City ~8,3 MB), mantendo
   hashes, proveniência e compatibilidade, antes de ampliar uso.
6. Só propor ML após definir alvo defensável, rótulos independentes, concordância
   dos avaliadores e baseline. Resultado da partida não rotula estratégia ideal;
   exigir split temporal e ganho real. Nenhum treinamento foi executado.

Documentos de referência: [viabilidade](V3_DATA_FEASIBILITY.md),
[contrato e fórmulas](REPORT_SCHEMA_V3.md), [conferência independente](V3_METRICS_CHECK.md)
e [changelog V2.2](CHANGELOG_V2_2.md).
