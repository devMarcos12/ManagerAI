# Arquitetura e contrato

> Este documento descreve o núcleo V1, preservado na V2. A extensão de apresentação
> e interface está em [CHANGELOG_V2.md](../CHANGELOG_V2.md) e no
> [tutorial V2](TUTORIAL_V2.md). Não houve mudança de schema ou de fórmulas.

O MVP reaproveita os JSONs locais e o conhecimento da EDA sem importar seus scripts,
que possuem configurações e saídas fixas. A biblioteca principal usa somente a
biblioteca padrão Python; Parquet, plotting e as dependências da EDA são opcionais
para atividades fora do fluxo do MVP.

```text
CLI → AnalysisRequest → catálogo validado → seleção temporal
    → carregamento dos jogos anteriores → features por jogo
    → perfis e comparação → regras documentadas → AnalysisReport
    → report.json + template report.md
```

| Arquivo em src/managerai | Responsabilidade |
|---|---|
| data_inventory.py | Catálogo, cobertura, equipes e reconciliação de arquivos sem vínculo |
| data_loader.py | Leitura protegida, validação estrutural básica e hashes das fontes |
| temporal.py | Seleção da janela sem alvo, futuro ou mesmo dia do corte |
| feature_engineering.py | Checagens de eventos, métricas por partida e agregação |
| tactical_analysis.py | Comparações e achados observáveis |
| recommendation_engine.py | Regras condicionais versionadas |
| report_schema.py | Dataclasses tipadas de entrada e saída; JSON sem NaN/Infinity |
| pipeline.py | Orquestração e auditoria de um recorte completo |
| report_renderer.py | Template português fiel ao relatório estruturado |
| cli.py / __main__.py | Interface de execução local e tratamento de erros |

## Entrada

`AnalysisRequest` exige competition_id, season_id, team_id, opponent_id e
**exatamente um** cutoff_date ou target_match_id. Os IDs devem existir no recorte;
as equipes devem ser diferentes; o alvo deve corresponder às duas equipes.
A data livre tem formato AAAA-MM-DD. Janela: inteiro 1–100, padrão 10.

Opcionais: venue, match_context, strategic_objective, unavailable_player_ids e notes.
Notas têm até 4.000 caracteres. Indisponíveis precisam ter sido observados nas
escalações anteriores da própria equipe dentro da janela selecionada. Não se usa
elenco da temporada inteira para validar dados disponíveis apenas depois do corte.

## Saída, schema_version 1.0.0

- `metadata`: IDs/nomes, corte, alvo, mando formal quando disponível, amostras
  solicitadas/analisadas, versão do software e fingerprint.
- `request`: entrada original, incluindo contexto manual.
- `team_profile` e `opponent_profile`: IDs das partidas, período, suficiência,
  métricas e contagens de qualidade.
- `comparison`: valores, diferenças equipe menos adversário, unidades, amostras e
  referências das evidências. A diferença é descritiva.
- `key_findings`: observações calculáveis, valores e limitações.
- `tactical_hypotheses`: regras acionadas, condições, evidências, riscos e limites.
- `formation_options` e `lineup_options`: arrays vazios neste baseline.
- `data_gaps`: lacunas detectadas e limites de inferência.
- `methodology`: políticas, versões e caminho/hash das fontes.

`MetricEvidence` contém metric_id, value anulável, unit, sample_size, match_ids,
numerator, denominator, median, standard_deviation, per_match e formula_version.
`per_match` preserva data, ID, valor e denominadores de cada observação elegível.
`TacticalHypothesis` referencia métricas com caminhos como
`opponent_profile.metrics.final_third_entries`.

Não há banco, servidor, endpoint remoto ou persistência além dos arquivos escolhidos
na CLI. A saída exige diretório novo e não pode ficar dentro da raiz dos dados.
Resultados originais não são sobrescritos. A execução não cria commits.

## LLM e evolução

A apresentação atual é um template determinístico, inclusive sem chave de API.
Não foi implementada chamada a LLM: sua adoção fica condicionada à escolha de
provedor, custo e política de fidelidade. O contrato estruturado já permite um
adaptador futuro; números e participantes devem continuar vindo exclusivamente
do relatório calculado. Não são necessárias dependências de OpenAI para este MVP.
