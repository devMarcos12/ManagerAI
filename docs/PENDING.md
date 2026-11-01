# ManagerAI — pendências e evidências

Atualização de 01/11/2026, com entrada por equipe sobre [`cccd25f`](https://github.com/devMarcos12/ManagerAI/commit/cccd25ff352ae5a2b7a85f6249b8c161f86b6a60). O estado funcional está em [CURRENT_VERSION.md](CURRENT_VERSION.md); este arquivo reúne decisões abertas, evidências essenciais e manifesto de limpeza. Cronologia completa anterior está preservada no Git, conforme §2. Não apresentar testes históricos como execução atual.

## 1. Prioridades

| Ordem | Pendência | Critério para concluir |
|---|---|---|
| 1 | Validação do novo fluxo por equipe e de `quality_v1` pelo usuário | Após pull/reinstalação, buscar time, conferir data/recorte, panorama sem adversário, contexto e comparação; depois conferir filtros/exclusões/abstenção/exportações, sem combinar V3 |
| 2 | CORE-01 no ambiente atual | Provisionar clone completo compatível e executar `verify-data`; os 762 arquivos da La Liga não substituem esse gate |
| 3 | Orientação e certificação CORE-02 | Revisão independente/vídeo e eventual protocolo prospectivo; não reduzir limiares após observar os resultados |
| 4 | Avaliação esportiva humana | Avaliadores identificados, rubrica, fontes/vídeo, justificativas e desacordos; medir correção, plausibilidade, clareza e utilidade separadamente |
| 5 | Generalização dos experimentos | Dados independentes/temporada futura e ganho útil pré-fixado; preditor de chutes não valida estratégia |
| 6 | Direitos e colaboração | Definir finalidade/distribuição, responsáveis nominais por dados/contratos/UI/avaliação e acesso da equipe aos backups/dados |
| 7 | Requisito acadêmico de IA | Confirmar com o professor se ajuste de explicação atende à tarefa exigida; não alegar aprendizado de decisão tática |

Serviço/API, frontend local e aproveitamento parcial básico estão implementados. CLI/Streamlit, fórmulas, contratos legados e adaptador V4.1 permanecem preservados. Não estão implementados motor tático aprendido, recomendação de escalação/formação ideal, eficácia causal ou uso analítico de 360. Expansão da política para V3, auditoria integral de Serie A/Ligue 1, autenticação/implantação pública e lock completo de transitivas são trabalhos separados, sem aprovação presumida.

## 2. Evidências e recuperação

A cronologia detalhada foi retirada dos documentos operacionais, sem apagar arquivos de evidência. Conteúdo integral, tabelas, comandos históricos, hashes e limitações continuam nestes snapshots imutáveis:

- [CURRENT_VERSION antes da consolidação](https://github.com/devMarcos12/ManagerAI/blob/f9315d91b82a8a3e3a91ecc1504d532c4248ade4/docs/CURRENT_VERSION.md): 495 linhas, SHA-256 `1eb8de34a7c0e6b5a68cafc8b4a009d9b410cd87b7b399ec95c4799244182e7f`.
- [PENDING antes da consolidação](https://github.com/devMarcos12/ManagerAI/blob/f9315d91b82a8a3e3a91ecc1504d532c4248ade4/docs/PENDING.md): 1.154 linhas, SHA-256 `f5b52e0694340f555a98252f1b455f45e7e7c224b913c837abf296ddf7be6ee4`.

As antigas referências a PENDING §3–§24 se referem a esse snapshot, não à numeração deste documento. No snapshot: V4.1 §3/§6; inventário/protocolo V4.2 §7–§13; A/B §14; robustez C §15; CORE-00 §16; provisionamento §17; matriz/certificação §18; UI §19; IA/backend §20; frontend §21; auditoria La Liga §22; famílias §23; qualidade no serviço §24. Consultar somente o trecho necessário. Nenhuma autorização antiga é reativada por esses links.

Recuperação de um documento sem sobrescrever o checkout atual:

```bash
git show f9315d91b82a8a3e3a91ecc1504d532c4248ade4:docs/PENDING.md
```

Usar o snapshot para consulta/comparação, não para restaurar automaticamente instruções superadas. Evidências pequenas versionadas permanecem em [research_evidence.json](research_evidence.json), [core_ai_protocol.json](core_ai_protocol.json), [tactical_review.schema.json](tactical_review.schema.json), [season_coverage_core02.json](season_coverage_core02.json) e [core02_laliga_201516_audit.json](core02_laliga_201516_audit.json). Pesos, datasets e execuções em `outputs/runs/` são locais/ignorados e não acompanham git pull. Campos de disponibilidade no resumo de pesquisa são históricos, não prova de presença nesta máquina.

Backups da limpeza histórica de 17/10/2026, registrados em `/home/marcos-junior/ManagerAI-backups/`:

| Pacote | SHA-256 registrado |
|---|---|
| `ManagerAI-history-13c50e5-20261017.tar.gz` | `48a57a602895eba21526ead7a53495520263989881aa19cdfaa082d3de9cf236` |
| `ManagerAI-history-phase3-13c50e5-20261017.tar.gz` | `8930e55539ed6510ecb43a6e73ae6db02086086609bfcb7c203886ce50e9efd1` |

Esses backups preservam os 29 arquivos históricos C retirados naquela fase; disponibilidade e hashes foram conferidos na execução histórica, não reconferidos neste ambiente. Antes de recuperar: conferir pacote/arquivo lateral, listar membros, extrair somente em diretório temporário novo com `--keep-old-files --no-same-owner` e validar `SHA256SUMS`/`MANIFEST.json`. Não extrair sobre o projeto. O snapshot EDA `docs/history/requirements-eda-20261017.txt`, SHA-256 `cda85b3a30d5094ec44bc285b580cecb195047f9fa7ff43bee6994a811e9453b`, permanece histórico, sem autoridade de instalação operacional.

## 3. Evidências da versão em uso

A tabela registra execuções anteriores à limpeza, com seus limites. Esta consolidação não executa treinamento, nova auditoria integral ou avaliação esportiva.

| Execução | Resultado preservado | Limite |
|---|---|---|
| Qualidade, fonte mínima, 01/11 | 315 descobertos: 262 aprovados, 53 pulados, zero falhas/erros; 3,577 s | Biblioteca padrão, sem opcionais |
| Qualidade, wheel instalado + API + La Liga, 01/11 | 315 descobertos: 272 aprovados, 43 pulados, zero falhas/erros; 8,165 s | Sem snapshot completo e demais opcionais; 49 módulos instalados iguais aos fontes |
| Qualidade, focais instalados, 01/11 | 13/13 qualidade e 14/14 elegibilidade | Fixtures sintéticas e casos reais delimitados |
| Qualidade, navegador portátil, 01/11 | 17/17, 18,2 s | API mockada, dois workers |
| Qualidade, navegador/API instalada/dados reais, 01/11 | 3/3, 13,4 s; JSON exportado igual à resposta; Markdown com exclusões | Sem mocks, desktop 1440×1000/mobile 390×844, sem erro JS/transbordamento |
| Frontend V3, 31/10 | Fluxos reais, evidências/gráficos/downloads e ciclo de falhas validados; detalhes no snapshot §21 | Medições locais não são SLA nem avaliação humana de utilidade |
| Backend/IA, 31/10 | 282 testes instalados completos e 16 comparações independentes aprovados; três inferências Ollama reais | Resultado histórico daquele ambiente, não reexecutado na limpeza |
| CI de `f9315d9` | [Três jobs aprovados](https://github.com/devMarcos12/ManagerAI/actions/runs/41325074934) | Wheel core, opcionais e frontend; sem StatsBomb |

Os três casos reais de qualidade são reproduzíveis em `frontend/tests/quality.real.ts`, com opt-in e servidores/dados configurados conforme [BACKEND_API.md](BACKEND_API.md):

| Caso | Resultado esperado sob a política atual |
|---|---|
| Real Madrid × Barcelona, alvo 267533, H10 | R03_CHANCES; finalizações/pressão n=10; direcionais n=0 |
| Málaga × Granada, alvo 3825672, H10 | Pressão do Granada n=9, excluindo 3825665 por duração; finalizações n=10; R03_CHANCES |
| Clássico, alvo 267533, janela 1 | HTTP 200 descritivo, sem planos; insuficiência explícita |

Artefatos da execução: `outputs/runs/core02_quality_service_20261101/`, com respostas e `final_validation.json`; capturas/logs em `/tmp/managerai-quality-*`. O resumo JSON versionado preserva código/hash, amostras e resultados essenciais. Tentativas iniciais com fixture incompleta, tipo do cliente e provisionamento/processo do navegador foram corrigidas; as contagens da tabela pertencem às execuções finais aprovadas. Histórico das falhas/limites no snapshot §24.

## 4. IA e decisões científicas

O sistema de produção calcula indicadores e planos por regras. Qwen2.5 1.5B via Ollama foi usado como explicador opcional restrito à seleção de IDs de afirmações; não escolhe tática, não recalcula indicadores e não recomenda atletas. Inferência real em três casos, incluindo insuficiência e injeção em notas, foi validada em 31/10. O modo sem LLM permanece disponível.

Experimentos quantitativos preveem **finalizações do mandante nos períodos 1/2**, com dois atributos H5: média própria de finalizações e média de finalizações concedidas pelo adversário. Atributos são congelados antes de carregar labels; sem alvo/dia do alvo/futuro/reposição, sem shuffle. Scaler e pesos usam só treino. Janelas e clubes compartilhados implicam dependência; não houve IC/p-valor IID nem validação de eficácia tática.

| Estudo histórico | Amostra/protocolo | Decisão e resultado essencial |
|---|---|---|
| A/B, PL 2015/16 | 330 exemplos/50 excluídos; treino/validação/teste 198/65/67 | Teste MAE B1=4,382090; OLS=4,092347; Ridge=4,091673. Ridge −6,6273% contra B1, sem superioridade estatística demonstrada |
| Robustez C, PL 2015/16 | 273 partidas únicas nov/2015–mai/2016 por esquema; expansivo e móvel90, 14 origens | MAE B1=4,124176; OLS/Ridge expansivo=3,994988/3,995920; móvel90=4,074797/4,073650. Ganho pequeno/sensível ao período, viés negativo; estudo pós-A/B exploratório |
| Entre competições, mesmo período | Treino PL n198 até 06/02/2016; teste La Liga n69 desde 09/04/2016 | MAE B0=3,9130434783; B1=3,3869565217; OLS=3,3503165445; Ridge=3,3504899821. Não atingem simultaneamente 0,2 chute E 5% contra B1; nenhum promovido |

Artefatos completos locais: `outputs/runs/v43_ab_pl2015_16_20261017/run.json`, `outputs/runs/v43_c_pl2015_16_20261017/run.json` e `outputs/runs/core_ai_independent_installed_20261031/evaluation.json`. O acervo completo pode não existir em outro checkout. Protocolo/configuração e hashes de resultados estão no código/JSONs versionados; robustez valida assinatura numérica a oito casas, sem modificar números armazenados, e permite reconstruir a referência A/B. Comandos no [README](../README.md#reproduzir-os-experimentos); detalhes, tabelas e sensibilidades no snapshot §14/§15/§20.

Fine-tuning de explicação: SmolLM2-135M-Instruct, revisão `12fd25f77366fa6b3b4b768ec3050bf629380bac`, LoRA r8/alpha16 em q_proj/v_proj, seed42, duas épocas, lr0,0005, 768 tokens, quatro threads CPU. Supervisão sintética de seleção de afirmações: 96 treino/24 validação/40 teste, particionados antes das derivações; 460.800 parâmetros treináveis, 192 passos. Validade/cobertura exata no teste: base 0%, ajustado 100%, template 100%. Ajustado foi salvo/recarregado, mas não demonstrou vantagem sobre template nessa tarefa, clareza/utilidade humana ou decisão tática aprendida; permanece experimental, fora da API de produção.

Adaptador histórico `adapter_model.safetensors`: SHA-256 `691444b0e23489dbb49c8ef1e9d6a45e9431e2a7b720fa151c3a8b99c571602d`, em `outputs/runs/core_ai_lora_20261031/adapter/`. O primeiro manifesto não capturou código no lançamento; a fonte foi reconstruída explicitamente em `executed_explainer_training.py`, SHA-256 `68aedc24299a76d74c82d63e8370dcc6eb272fe9e65ee6f12ab56783de5bd18c`, sem alterar dados/configuração/resultados. O runner entregue captura código para novas execuções. Não ocultar esse limite de proveniência. Protocolo canônico: `8cc07c14063e05c196e4815d24f03e22687d1c9f05f7ab30a897f1a50aa3cddc`.

[research_evidence.json](research_evidence.json) preserva configurações/resultados/hashes. `scripts/check_research_evidence.py --check` confere artefatos locais quando presentes; não regenerar o resumo para transformar ausência local em mudança do resultado histórico. Não treinar novamente durante limpeza. Revisão humana e adequação ao requisito acadêmico continuam abertas; a rubrica em [tactical_review.schema.json](tactical_review.schema.json) não é uma avaliação preenchida.

## 5. CORE-02 e certificação

A [matriz global](season_coverage_core02.json) registra presença/calendário de 80 pares. H5/H10 de calendário não é calculabilidade nem certificação. A auditoria integral de conteúdo da La Liga 2015/16 usou 762 arquivos oficiais da revisão fixada, com tamanho/SHA Git e SHA-256 conferidos: 380 eventos, 380 escalações, catálogo e calendário, 1.129.450.550 bytes; 1.295.354 eventos examinados. O clone completo não foi provisionado neste ambiente; não se obteve `verify-data=compatível` nem se substituiu a matriz anterior.

**La Liga 2015/16 não certificada.** Seis partidas têm falhas: 266106, 266467, 266961, 267273 (geometrias); 3825665, 3825875 (duração). Conferência independente reproduziu 9 posições iniciais inválidas, 17 destinos inválidos e 2 durações negativas; campos podem pertencer ao mesmo evento. Há 33/50 métricas calculáveis em todos os 760 jogos/equipe, mas zero janelas com todos os 50 indicadores em cada jogo histórico. `under_pressure` ausente continua distinto de False explícito; a métrica de ausência explícita é indisponível nos 760 jogos/equipe.

A política diagnóstica `metric-eligibility-1` agrupa 50 métricas em 16 famílias. Finalizações e passes globais têm H5/H10=330/280; pressão/recuperações por90 têm 314/254; qualidade de finalizações 325/270. Sequências: 507/760 jogos/equipe e H5/H10=2/0. Esses totais não são amostras independentes nem comprovam utilidade tática. Os seis jogos conservam finalizações/acerto global de passe elegíveis sob o diagnóstico. Campos, bloqueios, IDs e famílias completas estão em [core02_laliga_201516_audit.json](core02_laliga_201516_audit.json), não foram recalculados nesta limpeza.

Orientação: 1.141 grupos coerentes, 151 inconclusivos, 228 mistos, nenhum invertido. Todos os mistos têm mediana de chutes x≥80 e fração de movimentos crescentes abaixo de60%; todos os inconclusivos têm menos de três chutes, nenhum menos de dez movimentos. Circulação para trás pode refletir estilo; a guarda não prova coordenada invertida nem valida a direção real de cada evento. `orientation-review-1` mantém limiares; fonte primária e limites em [CORE02_CERTIFICATION.md](CORE02_CERTIFICATION.md). Mudança de protocolo exige avaliação independente, sem recalibração retroativa para aprovar este recorte.

O aproveitamento parcial `quality-report-1` é uma migração explícita do serviço básico, não da certificação. Não combina com V3, usa somente indicadores básicos ativos e bloqueia famílias direcionais fora da allowlist. Suficiência própria de cinco indicadores, exclusões e contrato separado estão em [CURRENT_VERSION.md](CURRENT_VERSION.md#6-serviço-qualidade-e-motores) e [BACKEND_API.md](BACKEND_API.md#filtros-de-qualidade-opcionais). CLI/Streamlit e V4.1 continuam com seus contratos anteriores. Snapshot completo permanece declarado `not_checked`.

## 6. Manifesto da limpeza

**Estado: consolidação documental e exclusão física concluídas.** Após a publicação de `c910f33`, o usuário aprovou explicitamente o manifesto abaixo; os 59 arquivos foram removidos com conferência de tamanho/SHA-256 antes de cada exclusão e backup preservado. Entrada `f9315d9`, 254 arquivos rastreados e 191.599.327 bytes. EDA protegida: 108 arquivos/174.432.856 bytes (91,04% dos bytes rastreados). Os documentos CURRENT_VERSION/PENDING tinham 1.649 linhas e 254.772 bytes; a redução desta etapa retira cronologia repetida do contexto operacional, preservando o conteúdo integral no Git.

Escopo executado: consolidar os dois documentos, corrigir referências dos guias/README/AGENTS e retirar comentários genéricos do `.gitignore` **sem alterar nenhum dos 102 padrões nem sua ordem**. Nenhum fonte, teste, fórmula, dependência ou contrato de aplicação muda.

### Arquivos preservados

- Todos os `src/`, `tests/`, `frontend/src/`, testes reais/portáteis, lockfiles, OpenAPI e tipos gerados; CLI/Streamlit continuam ativos.
- EDA completa `outputs/statsbomb_eda_20261002_exec6/` e seus scripts. Lotes e intermediários não foram classificados como descartáveis sem migração própria.
- Os três `report.json` em `outputs/mvp_demo_city_arsenal/`, `outputs/v3_demo_city_arsenal/` e `outputs/v3_demo_real_madrid_barcelona/`: fixtures consumidas por testes/proteções de saída. Seus Markdown/figuras também são exemplos referenciados pelo README.
- `outputs/v22_v3_validation/` e `outputs/v3_feasibility/`: evidências/verificadores independentes; nomes de versão não são motivo de exclusão.
- StatsBomb, licenças/atribuição, `outputs/runs/`, pesos, resultados científicos e backups; não apagar logs só pela extensão ignorada.
- Placeholders `data/raw/`, `data/processed/` e configuração compartilhada `.vscode/settings.json`: nenhum benefício ou decisão de equipe justificou sua retirada.

### Exclusões aprovadas e executadas

Foram removidos somente os **59 arquivos gerados** listados abaixo, total **693.739 bytes** (aproximadamente 678 KiB). São cópias de build/metadados de empacotamento e bundle web reconstruível; não são a dependência instalada no venv, o código-fonte ou as evidências científicas.

| Diretório | Arquivos exatos | Bytes |
|---|---:|---:|
| `build/` | 50 | 409.118 |
| `src/managerai.egg-info/` | 6 | 13.510 |
| `frontend/dist/` | 3 | 271.111 |

A aprovação ficou restrita aos caminhos listados, sem exclusão recursiva de diretórios, glob ou `git clean`. Cada arquivo teve caminho/bytes/SHA-256 reconferidos imediatamente antes da remoção; nenhum arquivo novo fora da lista foi removido. Uma futura limpeza exige inventário próprio. Este manifesto descreve este checkout de trabalho; git pull não apaga gerados ignorados na máquina do usuário. Em outro checkout, preparar inventário/backup próprio antes de pedir aprovação.

<details>
<summary>Lista exata dos 59 arquivos removidos</summary>

```text
build/lib/managerai/__init__.py
build/lib/managerai/__main__.py
build/lib/managerai/api.py
build/lib/managerai/cli.py
build/lib/managerai/coverage.py
build/lib/managerai/data_inventory.py
build/lib/managerai/data_loader.py
build/lib/managerai/experiments/__init__.py
build/lib/managerai/experiments/artifacts.py
build/lib/managerai/experiments/dataset.py
build/lib/managerai/experiments/explainer_training.py
build/lib/managerai/experiments/independent.py
build/lib/managerai/experiments/models.py
build/lib/managerai/experiments/paths.py
build/lib/managerai/experiments/robustness.py
build/lib/managerai/experiments/robustness_diagnostics.py
build/lib/managerai/experiments/runner.py
build/lib/managerai/explanation.py
build/lib/managerai/feature_engineering.py
build/lib/managerai/http_schema.py
build/lib/managerai/metric_eligibility.py
build/lib/managerai/options.py
build/lib/managerai/pipeline.py
build/lib/managerai/presentation/__init__.py
build/lib/managerai/presentation/coach_report.py
build/lib/managerai/presentation/terminology.py
build/lib/managerai/quality_report.py
build/lib/managerai/recommendation_engine.py
build/lib/managerai/report_renderer.py
build/lib/managerai/report_schema.py
build/lib/managerai/season_audit.py
build/lib/managerai/service.py
build/lib/managerai/service_schema.py
build/lib/managerai/statsbomb_provisioning.py
build/lib/managerai/statsbomb_snapshot.json
build/lib/managerai/streamlit_ui.py
build/lib/managerai/sufficiency.py
build/lib/managerai/tactical_analysis.py
build/lib/managerai/tactical_engine_schema.py
build/lib/managerai/tactical_engines.py
build/lib/managerai/temporal.py
build/lib/managerai/ui_support.py
build/lib/managerai/v3_features.py
build/lib/managerai/v3_history.py
build/lib/managerai/v3_pipeline.py
build/lib/managerai/v3_plots.py
build/lib/managerai/v3_presentation.py
build/lib/managerai/v3_rules.py
build/lib/managerai/v3_schema.py
build/lib/managerai/v3_sequences.py
frontend/dist/assets/index-Cgj8IgAM.js
frontend/dist/assets/index-RpkkbL39.css
frontend/dist/index.html
src/managerai.egg-info/PKG-INFO
src/managerai.egg-info/SOURCES.txt
src/managerai.egg-info/dependency_links.txt
src/managerai.egg-info/entry_points.txt
src/managerai.egg-info/requires.txt
src/managerai.egg-info/top_level.txt
```

</details>

### Rollback preparado e conferido

Manifesto local completo: `outputs/runs/cleanup_20261101/removal_manifest.json`, com caminho/tamanho/SHA-256 de cada arquivo, status concluído após aprovação e 59 removidos. O diário `removal_execution.json`, no mesmo diretório, registra aprovação, hashes de origem e cada remoção. Backup: `outputs/runs/cleanup_20261101/generated_rollback.tar.gz`; SHA-256 `6350c9a413167d6742d8145af28379ac02281c24ce8d5ffced1e23c393f7630d`. A extração em diretório temporário novo foi testada e todos os 59 hashes coincidiram. O backup está fora dos três diretórios candidatos, ignorado pelo Git, e não acompanha git pull; sua presença e o conteúdo dos 59 membros foram reconferidos antes da exclusão e o pacote foi mantido após a execução.

Restauração deve extrair primeiro em pasta nova, conferir os 59 hashes contra o manifesto e copiar somente caminhos aprovados ausentes, sem sobrescrever trabalho novo. Builds podem ser regenerados com empacotamento Python e `npm run build`, mas a cópia de rollback é a referência para recuperar os bytes antigos. O estado documental anterior pode ser consultado pelo commit do §2. Não há exclusão pendente de fonte/teste/fixture/EDA neste manifesto.

## 7. Validação desta limpeza

### Consolidação documental, antes da aprovação

Executado com Python 3.12.14 e sem alterar dependências:

- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -B -S -m unittest discover -s tests -q`: **315 descobertos, 262 aprovados, 53 pulados**, zero falhas/erros; 3,526 s. Log em `/tmp/managerai-cleanup-20261101-tests.log`. Pulos de opcionais/dados não contam como aprovação.
- **54 links locais e âncoras** nos documentos operacionais/guias válidos; snapshots anteriores conferidos contra hashes dos blobs Git de `f9315d9`.
- **102 padrões de ignore idênticos e na mesma ordem**; todos os caminhos ignorados anteriores continuam ignorados. Novos arquivos de preparação ficam exclusivamente no diretório ignorado desta limpeza.
- Na preparação, os **59 candidatos estavam intactos**, com rollback e restauração byte a byte conferidos. Nenhuma exclusão havia sido executada antes da aprovação.
- Três relatórios congelados mantêm os SHA-256 de entrada. Diff vazio em fontes, testes, frontend, scripts, dependências, atributos Git/CI e todo `outputs/` rastreado; EDA preservada. Alterações preexistentes foram mantidas.
- `git diff --check` passou. Inventário, baseline, manifesto e verificações em `outputs/runs/cleanup_20261101/`; esses artefatos locais não entram no commit.

Não foram reexecutados build, navegador, UI/V3, auditoria integral, LLM ou treinamento nesta execução local. As execuções funcionais do §3 continuam identificadas como históricas. A [CI da consolidação documental](https://github.com/devMarcos12/ManagerAI/actions/runs/41331758918) passou nos três jobs.

### Exclusão após aprovação

Os 59 arquivos aprovados foram removidos; nenhum arquivo rastreado foi excluído. Backup com SHA-256 conferido, membros do arquivo de rollback iguais ao manifesto e diário completo em `outputs/runs/cleanup_20261101/removal_execution.json`. Os diretórios vazios foram mantidos; nenhuma remoção recursiva foi usada. Validação posterior à exclusão, com Python 3.12.14:

- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -B -S -m unittest discover -s tests -q`: **315 descobertos, 262 aprovados, 53 pulados**, zero falhas/erros; 3,806 s. Log em `/tmp/managerai-cleanup-approved-20261101-tests.log`.
- **55 links locais e âncoras válidos**; `git diff --check` passou. Os 59 caminhos removidos continuam ausentes e os 59 membros do backup mantêm os hashes do manifesto.
- Três fixtures congeladas, 102 padrões de ignore e arquivos preexistentes preservados; diff vazio nos fontes/testes/frontend/scripts/dados/evidências rastreados. O único delta versionado é o registro desta conclusão nos dois documentos operacionais.

Verificações completas em `outputs/runs/cleanup_20261101/post_removal_validation.json`. Nenhum build foi executado para evitar recriar os gerados removidos. Esta exclusão é local ao checkout de trabalho; não limpa arquivos ignorados na máquina do usuário por git pull.

## 8. Validação da entrada por equipe

Entrega local de 01/11/2026 sobre `cccd25ff352ae5a2b7a85f6249b8c161f86b6a60`.
Implementação e validação concluídas. Publicação dos 25 arquivos desta entrega
no `main` autorizada explicitamente pelo usuário em 01/11/2026.
Busca global, resolução explícita de recorte, panorama individual e comparação
opcional implementados. Não houve migração de fórmulas, novos planos táticos,
certificação, treinamento ou ampliação da base. Nenhum arquivo de dados/evidência
existente foi alterado. Os três relatórios congelados usados na compatibilidade
foram obtidos do commit de referência com hashes Git conferidos.

Validação executada nesta entrega, sem reutilizar contagens históricas:

- Python 3.12.14, API em ambiente temporário novo: **326 testes descobertos,
  281 aprovados, 45 pulados, zero falhas/erros**, tanto nos fontes quanto no pacote
  instalado isoladamente de uma cópia temporária de empacotamento.
  Comandos: `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 /tmp/managerai-coach-venv/bin/python -B -m unittest discover -s tests -q`
  e `/tmp/managerai-coach-venv/bin/python -I -B -m unittest discover -s tests -q`.
  Os 11 novos testes cobrem equivalência individual, corte temporal, ausência sem
  reposição, nulos, temporadas separadas, catálogo parcial, validação e limites
  compartilhados da API. Pulos pertencem a opcionais/dados reais indisponíveis.
- Node 24.22.1, lockfile original: `npm ci`, `npm run build`, `npm run types:check`
  e exportação/conferência OpenAPI. Sem mudança de dependências do projeto.
- Playwright 1.64.1 com Chromium 153 temporário: **24/24 testes portáteis
  aprovados**, API mockada, incluindo sete testes novos do fluxo por equipe.
  A execução final usa `PLAYWRIGHT_BROWSER_EXECUTABLE_PATH=/tmp/managerai-chromium/chromium MANAGERAI_TEST_OUTPUT=/tmp/managerai-coach-playwright-final npm test`.
- API instalada + navegador, sem mocks e com fixture sintética identificada:
  panorama individual HTTP 200, comparação HTTP 200, contexto preservado,
  mesmo histórico entre panorama/comparação e JSON exportado igual à resposta.
  Desktop 1440×1000 e celular 390×844, sem erro JavaScript ou transbordamento.
  Artefatos temporários: `/tmp/managerai-coach-browser-check.json`,
  `/tmp/managerai-coach-desktop.png` e `/tmp/managerai-coach-mobile.png`.

Falhas de preparação resolvidas antes das execuções finais: pip inicial atualizado
somente no ambiente temporário; fixtures grandes recuperadas e verificadas por
hash sem regeneração; teste numérico ajustado para tolerância de ponto flutuante;
teste de teclado passou a aguardar a interface antes de pressionar Tab. A instalação
padrão de Chromium não estava disponível; o executável temporário alternativo não
alterou o lockfile nem as dependências do projeto.

Limites: sem clone StatsBomb completo, integração opt-in com dados reais,
certificação esportiva, avaliação por treinador, LLM ou treinamento nesta execução.
O panorama individual usa as fórmulas básicas sem `quality_v1`; aplicar a política
por família ao panorama é uma extensão futura separada, não uma certificação.
Os testes reais de frontend foram adaptados à busca por time, mas não executados
com StatsBomb nesta máquina. A validação manual pelo usuário permanece prioritária.

## 9. Gemini e .env pessoal

Entrega local sobre `c3a6bbb46f15ca0b49061c80483ac9a818f05d0c`, em 01/11/2026.
Criados modelo `.env.example`, gerador privado sem sobrescrita e leitura de `.env`
no backend com precedência do ambiente. `.env`/variantes ignorados; exemplos sem
credenciais compartilháveis. Cada instalação/backend usa sua própria chave; não
é autenticação multiusuário. O arquivo local nasceu sem chave e com ativação
`false`. Nenhuma chave compartilhada em conversa foi copiada para fontes/testes,
logs, exemplos, artefatos ou publicação.

Gemini acrescenta sugestões exploratórias independentes dos planos determinísticos.
Só indicadores elegíveis e contexto são enviados; notas/elenco/brutos não entram.
Formato, citações, amostra por indicador e ausência de algarismos na prosa são
checados, sem prova semântica ou validação esportiva. Números ficam materializados
pelas evidências do Core. Bloqueios manuais/amostra insuficiente produzem abstenção.
Cache volátil, pausa após 429, sem retries, upgrades ou fallback de provedor/modelo.
A integração não verifica o faturamento Google; o operador precisa confirmar o
plano gratuito antes de ativar. A chave precisa ser configurada em cada máquina.

Validação nesta entrega:

- Python 3.12.14 com API, fontes: **338 descobertos, 293 aprovados, 45 pulados**,
  zero falhas/erros. Após acrescentar a integração HTTP/exportação ao teste focal:
  **13/13 testes Gemini/.env aprovados**; pacote instalado isoladamente:
  **339 descobertos, 294 aprovados, 45 pulados**, zero falhas/erros.
- Comandos: `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 /tmp/managerai-coach-venv/bin/python -B -m unittest discover -s tests -q`,
  focal `-m unittest test_gemini -q`, instalado
  `/tmp/managerai-coach-venv/bin/python -I -B -m unittest discover -s tests -q`.
- Node 24.22.1, lockfile preservado: tipos, `npm run build`, `npm run types:check`
  e OpenAPI conferidos. Playwright/Chromium temporário: **27/27 aprovados**, API
  mockada, incluindo sugestões, referências, desligamento e cota sem repetição.
- Git `check-ignore` em repositório temporário: cinco variantes de `.env` locais
  ignoradas, `.env.example` e `frontend/.env.example` compartilháveis. Gerador
  confirmou arquivo novo com modo 0600 e preservação de conteúdo existente.
- Erro inicial de identidade legado corrigido preservando a serialização de
  pedidos sem IA; teste de qualidade voltou a passar sem mudar o fixture/hash.
  Demais ajustes de preparação: import React e default da fixture HTTP corrigidos.

Logs temporários em `/tmp/managerai-gemini-*.log`. Não houve inferência externa,
validação da chave real, gasto em API, execução Ollama/treinamento ou integração
com StatsBomb real. A API instalada foi testada com provedor fictício, incluindo
exportação JSON igual à resposta e Markdown com sugestões/citações. Pulos não
contam como aprovação. Validação humana e ensaio com chave nova em projeto
Google comprovadamente gratuito permanecem pendentes.
