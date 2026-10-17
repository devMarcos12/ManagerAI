# ManagerAI — pendências e manifesto de limpeza

Atualizado em 17/10/2026. Estado/contratos/comandos: [CURRENT_VERSION.md](CURRENT_VERSION.md). Regras: [AGENTS.md](../AGENTS.md). **Fase 1 concluída: os 29 arquivos do grupo A e os dois diretórios vazios autorizados foram removidos. Os grupos B (38 arquivos) e C (29 arquivos) permanecem intactos, aguardando nova aprovação.** README, código funcional, testes, dados e documentação das outras versões não foram alterados. Resultados desta execução na seção 6.

## 1. Prioridades, dependências e conclusão

| ID | Prioridade / status | Trabalho e dependências | Critério de conclusão |
|---|---|---|---|
| DOC-01 | P0 / CONCLUÍDO | Consolidar estado e regras a partir da auditoria integral, código, contratos e testes | `CURRENT_VERSION.md`, este arquivo e `AGENTS.md` preparados; nenhuma alteração funcional |
| VAL-01 | P0 / CONCLUÍDO | Validar comportamento existente, imports, contratos, paths e links com dependências já presentes | Resultados reais na seção 2; testes/fixture preservados |
| CLEAN-01 | P0 / PARCIAL | Grupo A autorizado e executado na Fase 1; B/C e destino histórico continuam sem autorização | A: 29 removidos e dois diretórios vazios; B/C exigem decisão própria |
| DOC-02 | P1 / PENDENTE | Migrar links do README para os três documentos operacionais, exemplos finais e evidências; depende CLEAN-01 e autorização para editar README | README curto sem links quebrados; retirar antigos documentos somente após checar cobertura |
| CLEAN-02 | P1 / FASE 1 CONCLUÍDA; B/C PENDENTES | Grupo A encerrado; não iniciar B/C sem aprovação, DOC-02, backup e migração das referências | Fase 1: 135 testes antes/depois, 16 comparações antes/depois e links íntegros |
| DATA-01 | P1 / DECISÃO HUMANA | Definir provisionamento do clone StatsBomb e recuperação; sem mover dados/EDA | Revisão fixa, licença, responsável e recuperação testável para outro integrante |
| ENV-01 | P1 / PENDENTE | Separar requisitos diretos/runtime/EDA e preservar snapshot; decidir faixas/pins/lock antes de instalar algo | Núcleo sem extras, UI e V3 reproduzíveis; EDA preservada; nenhuma remoção automática de pacotes |
| ART-01 | P1 / PENDENTE | Política `.gitignore` de novas execuções e logs científicos; depende CLEAN-01 | Temporários separados de exemplos/fixtures/evidências, sem ignore amplo de `outputs/` |
| TEAM-01 | P2 / DECISÃO HUMANA | Definir responsáveis por contratos, indicadores/dados, UI e avaliação; decidir versionamento dos documentos locais | Responsabilidades e revisão compartilhadas; não integrar repositórios de colegas por inferência |
| REF-01 | P2 / NÃO INICIADO | Consolidar constantes de suficiência e revisar acoplamento regras/apresentação | Refatoração separada de limpeza, sem alterar resultados/schema/fórmulas |
| V3-01 | P2 / NÃO INICIADO | Auditar novas temporadas, orientação, campos e envelhecimento da evidência | Auditoria e testes próprios antes de ampliar `VALIDATED_RECUTS`; não juntar temporadas implicitamente |
| PERF-01 | P2 / NÃO INICIADO | Avaliar custo de JSONs V3 extensos e operações de releitura | Medição real e solução preservando contratos, hashes e inspeção de evidências |
| EVAL-01 | P1 / NÃO INICIADO | Aplicar revisão de hipóteses com especialistas/vídeo/treino | Correção, rastreabilidade, compreensão, plausibilidade, riscos e utilidade registrados separadamente; sem alegar causalidade |
| AI-01 | P3 / PLANEJADO, NÃO IMPLEMENTADO | Motor/modelo especializado: tarefa, entradas/saídas e métricas; depende EVAL-01, DATA-01 e baseline | Proposta e avaliação independentes antes de implementação; nenhuma capacidade aprendida existente |
| AI-02 | P3 / PLANEJADO, NÃO IMPLEMENTADO | Fine-tuning: alvos/rótulos, avaliadores/concordância, direitos e divisão temporal; depende AI-01 | Evidência de dados suficientes e ganho mensurável contra baseline; placar não é label de tática ideal |
| AI-03 | P3 / PLANEJADO, NÃO IMPLEMENTADO | LLM explicadora/adaptador de saída, provedor/custo/fidelidade | Números vindos do relatório determinístico, avaliação de fundamentação e abstenção; sem integração atual |
| AI-04 | P3 / NÃO IMPLEMENTADO, SEM ESCOPO APROVADO | Recomendações de escalação/formação ideal e disponibilidade | Fonte de disponibilidade, tarefa e validação próprias; não inferir de formações/atletas históricos |

`CONCLUÍDO` registra somente trabalho das fases já realizadas, identificado nas seções 2 e 6. `PENDENTE` não autoriza execução. Nenhum treinamento, fine-tuning, modelo especializado, integração LLM ou recomendação de escalação está implementado. A UI já se integra ao núcleo; essa integração não é uma pendência futura.

## 2. Validação da consolidação documental — anterior à Fase 1

Data: 17/10/2026, Python 3.12.3. Suíte principal com `venv/bin/python`, Streamlit 1.65.0 e Matplotlib 3.11.2 já disponíveis, sem instalar dependências. Saídas da validação capturadas no terminal, sem criar novos logs no projeto.

| Comando / contexto | Resultado observado |
|---|---|
| `MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg venv/bin/python -B -m unittest discover -s tests -v` | **135 aprovados**, 0 falhas, 0 erros, 0 pulos; 60,536 s na suíte; processo código 0 |
| `PYTHONPATH=src python3 -B -S -m unittest discover -s tests -v` | 135 descobertos: **110 aprovados**, 0 falhas, 0 erros, **25 pulados**, 1,271 s; código 0 |
| `PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py` | **16 comparações aprovadas**, oito métricas em dois jogos (3754320 e 3773585), catálogo 26; código 0 |

Na suíte principal, um `TemporaryDirectory` em `/tmp/managerai-doc-validation-*` foi usado para `TMPDIR`, `MPLCONFIGDIR=<tmp>/mpl`, `XDG_CACHE_HOME=<tmp>/cache` e `XDG_CONFIG_HOME=<tmp>/config`. Fixtures/figuras/relatórios transitórios foram geridos pelos testes. `-B` e `PYTHONDONTWRITEBYTECODE=1` impediram novos caches Python no projeto. Avisos Streamlit `missing ScriptRunContext` apareceram no AppTest, sem falhas. Não houve teste manual de navegador nem avaliação esportiva.

Os 25 pulos da execução `-S` correspondem a integrações locais desativadas e opcionais Streamlit/Matplotlib indisponíveis nesse modo; não contam como aprovação. A entrega histórica registrava 18 pulos com dados reais habilitados, contexto diferente. Não copiar contagens antigas para novos ambientes.

Conferência estática final: 47 arquivos Python com sintaxe válida; 63 links Markdown locais em AGENTS/README/changelog/docs, nenhum destino ausente; sete exemplos CLI de consulta/análise aceitos pelo parser; todos os 21 IDs legados e 26 IDs V3 presentes em `CURRENT_VERSION.md`, com recortes `(2,27)` e `(11,90)` confirmados por import. O manifesto A/B/C contém 96 caminhos existentes e distintos. Conferiram-se seleção temporal, dependências entre módulos, schemas e fixture consumida por três testes; a suíte exercitou imports e contratos em execução.

Comparação SHA-256 de 273 arquivos preexistentes do projeto (incluindo fontes, testes, outputs/EDA, documentação e caches; excluídos clone bruto, ambiente virtual e metadados Git): somente `AGENTS.md` mudou; nenhum arquivo ausente e apenas `CURRENT_VERSION.md`/`PENDING.md` acrescentados. `git diff --check` sem problemas rastreados; três documentos editados sem espaços finais e com cercas de código balanceadas. A auditoria anterior ficou intacta. Não se repetiu hash integral dos brutos, auditoria integral de todos os eventos, instalação limpa ou execução da EDA.

## 3. Decisões de consolidação

O plano abaixo substitui a proposta mais conservadora de conservar toda geração descrita em `REPOSITORY_AUDIT.md`. A auditoria permanece intacta como evidência da etapa anterior. **Versão diferente, isoladamente, não justifica conservar outro relatório.**

- Manter um baseline legado congelado: `outputs/mvp_demo_city_arsenal/report.json`.
- Manter dois exemplos finais V3 (normal e amostra insuficiente), cada um com JSON, Markdown e dois PNGs, listados em D. Eles representam comportamentos diferentes, não duplicação editorial.
- As definições dos dez contratos/guias de B1 foram consolidadas nas seções 1–7 de `CURRENT_VERSION.md`: módulos/fluxo, qualidade, 21+26 métricas, sequências/histórico, regras, JSON, comandos, testes e avaliação. Antes de removê-los, revisar a cobertura e migrar links; eventuais lacunas devem ser incorporadas ao documento atual primeiro.
- Casos antigos inspecionados: City alvo 3754314, janela 10, n=10/10, duas hipóteses legadas; janela 2, n=2/2, nenhuma; corte livre 2016-05-08, n=10/10; corte inicial 2015-08-08, n=0/0, nenhuma; Real alvo 3773497, n=1/10, nenhuma. São procedimentos/testes de regressão reutilizáveis, já consolidados no documento atual; não é necessário manter todos os relatórios gerados.
- Apresentações antigas MVP/V2/V2.2 diferem editorialmente; o formato vigente é o renderer atual. JSON City é idêntico em cinco pastas (incluindo baseline); JSONs de pouca amostra/sem histórico são idênticos entre MVP/V2. Não retirar os testes que reproduzem esses casos.
- Primeiras gerações `v3_city_arsenal` e `v3_real_madrid_barcelona`: JSON, Markdown e mapa de chutes são idênticos aos exemplos finais; somente gráficos de progressão diferem. O defeito era corte da escala superior, corrigido nas gerações `v3_demo_*` e protegido por teste de escala. Conservar fora do conjunto operacional somente esses dois PNGs como evidência visual específica; consolidar a explicação aqui antes de retirar os READMEs redundantes.
- Evidências científicas duráveis locais: `outputs/v3_feasibility/` e `outputs/v22_v3_validation/{check_metrics.py,independent_metrics.json,final_summary.json}`. Ferramentas e resultados permanecem nos caminhos atuais para não criar migração funcional desnecessária. C propõe arquivo externo apenas para histórico de execução que não precisa estar no contexto operacional.
- Dataset, licença e EDA original permanecem intactos; **não há proposta de mover a EDA nem seus scripts nesta limpeza**. Tirar esses caminhos do contexto automático já reduz ruído sem quebrar reprodução histórica.

### Migração de referências necessária

O README ainda liga tutoriais, contratos, specs, changelogs, exemplos V2 e EDA. Não foi editado na consolidação, e a Fase 1 também exige preservá-lo. DOC-02 deve apontar instruções/contratos para `docs/CURRENT_VERSION.md`, pendências para este documento, demos para `v3_demo_*` e evidências para caminhos mantidos ou arquivo histórico acessível, mediante autorização própria. Não publicar links para destino externo ainda não definido.

Specs têm referências cruzadas e autorizações antigas; `docs/architecture.md` aponta para tutorial/changelog V2. `V3_DATA_FEASIBILITY.md` liga `outputs/v3_feasibility/`; `V3_METRICS_CHECK.md` e `TUTORIAL_V3.md` ligam o script independente. Ao arquivar documentos, manter cópia legível e mapa dos links; executar busca global e validação de destinos antes da exclusão. Referências textuais no manifesto/auditoria registram caminhos antigos intencionalmente, não são chamadas operacionais.

## 4. Manifesto original — grupo A executado na Fase 1

Todos os caminhos são relativos à raiz e existiam no inventário da consolidação. As listas originais ficam preservadas para rastreabilidade: A enumera exatamente os 29 arquivos removidos na Fase 1; B/C continuam existentes e sem execução autorizada. As listas são fechadas: arquivos novos encontrados futuramente precisam de nova classificação. B exige migração e aprovação; C exige transferência verificada ao arquivo histórico e aprovação. Não usar globs como comando de remoção.

### A. Remoção segura — 29 arquivos removidos

**A1 — quatro arquivos removidos:** dois placeholders vazios sem consumidor funcional identificado e duas cópias idênticas do exemplo MVP. Identidade binária e referências verificadas antes da remoção; baseline original preservado e backup temporário preparado.

```text
src/extract.py
src/.gitkeep
outputs/meu_primeiro_teste/report.json
outputs/meu_primeiro_teste/report.md
```

JSON/Markdown de `meu_primeiro_teste` correspondem respectivamente aos SHA-256 de prefixos `424389e2af0a` e `52796d491771` do caso MVP. A busca em código/testes não encontrou consumidores dessa pasta; a auditoria e este documento a citam para inventário.

**A2 — 25 caches preexistentes removidos:** cada arquivo foi confirmado como cache CPython 3.12, com fonte correspondente preservada, sem consumidor essencial identificado. Os testes posteriores passaram sem esses caches e sem recriá-los. `venv/` permaneceu intacto.

```text
scripts/__pycache__/run_statsbomb_eda.cpython-312.pyc
src/managerai/__pycache__/__init__.cpython-312.pyc
src/managerai/__pycache__/coverage.cpython-312.pyc
src/managerai/__pycache__/data_inventory.cpython-312.pyc
src/managerai/__pycache__/data_loader.cpython-312.pyc
src/managerai/__pycache__/feature_engineering.cpython-312.pyc
src/managerai/__pycache__/pipeline.cpython-312.pyc
src/managerai/__pycache__/recommendation_engine.cpython-312.pyc
src/managerai/__pycache__/report_renderer.cpython-312.pyc
src/managerai/__pycache__/report_schema.cpython-312.pyc
src/managerai/__pycache__/streamlit_ui.cpython-312.pyc
src/managerai/__pycache__/tactical_analysis.cpython-312.pyc
src/managerai/__pycache__/temporal.cpython-312.pyc
src/managerai/__pycache__/ui_support.cpython-312.pyc
src/managerai/__pycache__/v3_features.cpython-312.pyc
src/managerai/__pycache__/v3_history.cpython-312.pyc
src/managerai/__pycache__/v3_pipeline.cpython-312.pyc
src/managerai/__pycache__/v3_plots.cpython-312.pyc
src/managerai/__pycache__/v3_presentation.cpython-312.pyc
src/managerai/__pycache__/v3_rules.cpython-312.pyc
src/managerai/__pycache__/v3_schema.cpython-312.pyc
src/managerai/__pycache__/v3_sequences.cpython-312.pyc
src/managerai/presentation/__pycache__/__init__.cpython-312.pyc
src/managerai/presentation/__pycache__/coach_report.cpython-312.pyc
src/managerai/presentation/__pycache__/terminology.cpython-312.pyc
```

Diretórios vazios opcionais, **não arquivos**: `data/mock/` e `src/utils/` foram confirmados vazios e removidos com `rmdir`, sem recursão. Nenhum outro diretório foi removido. Não têm efeito em Git, que não versiona diretórios vazios.

### B. Remoção condicionada à consolidação e migração

**B1 — dez documentos:** retirar após revisão de equivalência operacional com `CURRENT_VERSION.md`, DOC-02 e validação dos links. Risco médio/alto: perder detalhe técnico se revisão for incompleta; consolidar qualquer conteúdo faltante antes, sem criar outro manual operacional.

```text
docs/architecture.md
docs/data_dictionary.md
docs/metrics.md
docs/tactical_rules.md
docs/evaluation.md
docs/AVALIACAO_COMISSAO_TECNICA.md
docs/REPORT_SCHEMA_V3.md
docs/TUTORIAL_TESTES.md
docs/TUTORIAL_V2.md
docs/TUTORIAL_V3.md
```

**B2 — 19 arquivos de exemplos antigos:** procedimentos/casos já consolidados; preservar os testes, fixture e exemplos finais. Não alegar que todo Markdown/JSON é binariamente igual. Risco médio: links entregues e expectativas externas, principalmente README V2 e tutoriais; migrar referências primeiro e manter backup reversível da limpeza.

```text
outputs/mvp_demo_city_arsenal/report.md
outputs/mvp_demo_amostra_pequena/report.json
outputs/mvp_demo_amostra_pequena/report.md
outputs/mvp_demo_data_livre/report.json
outputs/mvp_demo_data_livre/report.md
outputs/mvp_demo_sem_historico/report.json
outputs/mvp_demo_sem_historico/report.md
outputs/v2_city_arsenal/report.json
outputs/v2_city_arsenal/report.md
outputs/v2_demo_city_arsenal/report.json
outputs/v2_demo_city_arsenal/report.md
outputs/v2_amostra_pequena/report.json
outputs/v2_amostra_pequena/report.md
outputs/v2_sem_historico/report.json
outputs/v2_sem_historico/report.md
outputs/v22_city_arsenal/report.json
outputs/v22_city_arsenal/report.md
outputs/v22_real_madrid_barcelona/report.json
outputs/v22_real_madrid_barcelona/report.md
```

**B3 — oito arquivos das primeiras gerações V3:** manter cópias finais em D; consolidar registro da revisão visual (seção 3) e arquivar os PNGs únicos de C3 antes. Risco médio: links dos READMEs apontam para finais e entrega antiga cita as primeiras gerações; migrar leitores e preservar ligação PNG inicial→final no manifesto de arquivo.

```text
outputs/v3_city_arsenal/README.md
outputs/v3_city_arsenal/report.json
outputs/v3_city_arsenal/report.md
outputs/v3_city_arsenal/shot_map.png
outputs/v3_real_madrid_barcelona/README.md
outputs/v3_real_madrid_barcelona/report.json
outputs/v3_real_madrid_barcelona/report.md
outputs/v3_real_madrid_barcelona/shot_map.png
```

**B4 — um arquivo pessoal a confirmar:** `.vscode/settings.json`. Contém só `python-envs.pythonProjects: []`, sem efeito funcional identificado. Risco baixo; retirar apenas se a equipe confirmar que não é configuração compartilhada necessária. Revisar `.gitignore` em tarefa posterior; ignorar arquivo rastreado não o retira do índice.

### C. Histórico que pode sair do conjunto operacional

Destino ainda exige decisão humana: armazenamento durável acessível à equipe, com prefixo `ManagerAI/13c50e5/` e **o mesmo caminho relativo de origem** sob esse prefixo. Não criar esse arquivo histórico agora. Salvar manifesto SHA-256/data/revisão/responsável e testar recuperação; preservar evidências datadas sem atualizar seus HEADs/resultados. Revisar links e conteúdo sensível de logs antes de compartilhar. Sem destino recuperável aprovado, estes arquivos ficam onde estão.

**C1 — nove documentos históricos:** guardar decisões/especificações e auditorias, em vez de mantê-los como novos manuais operacionais. As definições atuais e pendências estão consolidadas; métricas de auditoria detalhadas continuam evidência histórica acessível. Risco médio de perder contexto/proveniência se a cópia externa não for verificável.

```text
SPEC_MVP_ANALISE_TATICA_STATSBOMB.md
SPEC_V2_MANAGERAI_RELATORIO_INTERFACE.md
SPEC_V2_2_E_V3_MANAGERAI_EXECUCAO_AUTONOMA.md
CHANGELOG_V2.md
docs/CHANGELOG_V2_2.md
docs/RELATORIO_FINAL_V2_2_V3.md
docs/V3_DATA_FEASIBILITY.md
docs/V3_METRICS_CHECK.md
docs/REPOSITORY_AUDIT.md
```

**C2 — 18 arquivos de evidência de sessões anteriores:** não descartar logs/estados só por serem antigos ou iguais; retirar do operacional após cópia e acesso documentado. Risco alto para logs ignorados, pois o Git pai não os recupera. Ficam localmente `check_metrics.py`, `independent_metrics.json` e `final_summary.json`; não são itens deste lote.

```text
outputs/mvp_validation/audit_pl_2015_16.json
outputs/mvp_validation/inventory.json
outputs/mvp_validation/tests.log
outputs/v2_validation/summary.json
outputs/v2_validation/tests.log
outputs/v22_v3_validation/changed_code_files.json
outputs/v22_v3_validation/complete_tests.log
outputs/v22_v3_validation/dependency_check.txt
outputs/v22_v3_validation/final_git_status.txt
outputs/v22_v3_validation/final_head.txt
outputs/v22_v3_validation/initial_git_status.txt
outputs/v22_v3_validation/initial_head.txt
outputs/v22_v3_validation/preservation_and_reports.json
outputs/v22_v3_validation/stdlib_tests.log
outputs/v22_v3_validation/v22_baseline.log
outputs/v22_v3_validation/v22_tests.log
outputs/v22_v3_validation/v22_ui.log
outputs/v22_v3_validation/v3_ui_tests.log
```

**C3 — dois PNGs históricos específicos:** prova da escala inicialmente cortada, diferente do gráfico final. Risco médio; guardar metadados e relação com as imagens finais, sem reter cópias idênticas de JSON/Markdown/mapas só pela versão.

```text
outputs/v3_city_arsenal/progression_entries.png
outputs/v3_real_madrid_barcelona/progression_entries.png
```

**Inventário original:** A = 29 arquivos; B = 38 arquivos; C = 29 arquivos, total de 96 distintos. **Executado:** A e dois diretórios vazios. **Restam 67 candidatos sem autorização de execução:** 38 condicionados e 29 para futuro arquivo histórico verificável. Nenhum dos 67 foi alterado, removido ou movido nesta fase. Não confundir contagem de candidatos com número de arquivos rastreados.

### D. Arquivos obrigatórios e preservação

**Não candidatos:** todos os 26 `.py` ativos de `src/managerai/`, `streamlit_app.py` e os 14 módulos de teste enumerados em `CURRENT_VERSION.md`; nenhum teste será excluído. Manter `pyproject.toml`, `requirements-ui.txt`, `requirements-v3.txt`, `.streamlit/config.toml`, `.gitignore`, README e os três documentos operacionais. `requirements.txt` permanece até ENV-01 preservar o snapshot e validar a reorganização; não remover por conter Torch/CUDA/OpenAI.

Inventário explícito dos arquivos de código, testes e configuração mantidos:

```text
src/managerai/__init__.py
src/managerai/__main__.py
src/managerai/cli.py
src/managerai/coverage.py
src/managerai/data_inventory.py
src/managerai/data_loader.py
src/managerai/feature_engineering.py
src/managerai/pipeline.py
src/managerai/presentation/__init__.py
src/managerai/presentation/coach_report.py
src/managerai/presentation/terminology.py
src/managerai/recommendation_engine.py
src/managerai/report_renderer.py
src/managerai/report_schema.py
src/managerai/streamlit_ui.py
src/managerai/tactical_analysis.py
src/managerai/temporal.py
src/managerai/ui_support.py
src/managerai/v3_features.py
src/managerai/v3_history.py
src/managerai/v3_pipeline.py
src/managerai/v3_plots.py
src/managerai/v3_presentation.py
src/managerai/v3_rules.py
src/managerai/v3_schema.py
src/managerai/v3_sequences.py
tests/test_coverage.py
tests/test_local_data.py
tests/test_managerai.py
tests/test_presentation.py
tests/test_streamlit_ui.py
tests/test_v22_presentation.py
tests/test_v22_ui.py
tests/test_v3_features.py
tests/test_v3_history.py
tests/test_v3_integration.py
tests/test_v3_presentation.py
tests/test_v3_rules.py
tests/test_v3_sequences.py
tests/test_v3_ui.py
streamlit_app.py
pyproject.toml
requirements.txt
requirements-ui.txt
requirements-v3.txt
.streamlit/config.toml
.gitignore
README.md
AGENTS.md
docs/CURRENT_VERSION.md
docs/PENDING.md
data/raw/.gitkeep
data/processed/.gitkeep
scripts/run_statsbomb_eda.py
scripts/finalize_statsbomb_eda.py
scripts/gerar_docx_eda.py
```

Artefatos operacionais/científicos mantidos, caminhos exatos:

```text
outputs/mvp_demo_city_arsenal/report.json
outputs/v3_demo_city_arsenal/report.json
outputs/v3_demo_city_arsenal/report.md
outputs/v3_demo_city_arsenal/shot_map.png
outputs/v3_demo_city_arsenal/progression_entries.png
outputs/v3_demo_real_madrid_barcelona/report.json
outputs/v3_demo_real_madrid_barcelona/report.md
outputs/v3_demo_real_madrid_barcelona/shot_map.png
outputs/v3_demo_real_madrid_barcelona/progression_entries.png
outputs/v3_feasibility/audit.json
outputs/v3_feasibility/possession_decrease_example.json
outputs/v3_feasibility/reproduce_audit.py
outputs/v22_v3_validation/check_metrics.py
outputs/v22_v3_validation/independent_metrics.json
outputs/v22_v3_validation/final_summary.json
```

Preservação de conjuntos, sem propor movimentação de seus arquivos: `open-data/data/` inteiro, `open-data/{README.md,LICENSE.pdf,.git/}`, `outputs/statsbomb_eda_20261002_exec6/` inteiro, `scripts/run_statsbomb_eda.py`, `scripts/finalize_statsbomb_eda.py`, `scripts/gerar_docx_eda.py`, `data/raw/.gitkeep` e `data/processed/.gitkeep`. O `.DS_Store` dentro do clone externo não entra nesta autorização de limpeza. Manter `venv/` funcional; ignorá-lo no contexto é suficiente.

## 5. Ordem, rollback e decisões de aprovação

1. A já foi aprovado e executado exclusivamente na Fase 1. Para B/C, obter aprovação separada, confirmar consumidores externos e escolher destino histórico/responsável. Registrar HEAD/status e hashes antes de tocar nos arquivos. Backup deve incluir ignorados/não rastreados, em especial logs e clone externo; Git principal isoladamente não é rollback suficiente.
2. Migrar README e referências operacionais para `CURRENT_VERSION.md`, este documento, exemplos/evidências mantidos; revisar cobertura dos dez documentos B1. Este trabalho exige autorização adicional, pois README não foi editável nesta fase.
3. Após aprovação própria, transferir C com hashes e recuperação testada; consolidar registro visual e casos antes de retirar B. Aplicar B em lotes pequenos; o lote A está encerrado. Não usar `git clean`, `git reset` nem reescrever histórico.
4. Depois de cada lote, conferir links/imports/paths, fixture congelada, schemas, testes proporcionais e matriz completa quando afetar execução/testes. Se falhar, restaurar somente arquivos/referências do lote por cópias verificadas, sem apagar trabalho preexistente. Manter backup até aceite da equipe.
5. Atualizar os dois documentos de estado/pendências com o que foi efetivamente concluído. Remover as listas executadas do contexto diário somente após manter rastreabilidade no arquivo histórico. Não realizar commit/push sem autorização explícita.

Decisões pendentes: aprovar os 38 candidatos B e os 29 C (ou subconjunto), definir destino histórico recuperável, confirmar `.vscode/settings.json`, autorizar migração do README/links e revisão de `.gitignore`/ambientes, definir responsáveis por dados/contratos/avaliação e o escopo da futura IA. Os arquivos B/C continuam nos caminhos atuais; a próxima fase não foi iniciada.

## 6. Registro da limpeza controlada — Fase 1

Executada em 17/10/2026, por autorização explícita restrita a A1/A2 e aos dois diretórios opcionais vazios. Leitura de `AGENTS.md`, `CURRENT_VERSION.md`, deste manifesto e da auditoria integral antes da execução. HEAD inicial/final do ManagerAI: `13c50e5cc7e54e6f45487b89cdbe3994d621587f`.

### Estado inicial e escopo efetivo

`git status --short` inicial, sem mudanças rastreadas:

```text
?? AGENTS.md
?? docs/CURRENT_VERSION.md
?? docs/PENDING.md
?? docs/REPOSITORY_AUDIT.md
?? open-data/
```

Os 29 caminhos foram extraídos do grupo A e comparados, na ordem, com uma lista independente explícita. Cada candidato era arquivo regular dentro da raiz, sem link simbólico. Verificações individuais:

- `src/extract.py` e `src/.gitkeep`: zero bytes, sem import/caminho funcional consumidor encontrado; `src/` continua contendo código rastreado.
- `outputs/meu_primeiro_teste/report.json` e `report.md`: comparação byte a byte com os correspondentes de `outputs/mvp_demo_city_arsenal/`; originais preservados. As referências encontradas eram inventários desta documentação/auditoria e registros históricos de status Git, não consumidores ativos.
- Os 25 `.pyc`: assinatura CPython 3.12 e fonte `.py` correspondente existente, sem dependência de distribuição apenas por bytecode. Fontes preservadas; nenhum teste ou configuração exige esses caches específicos.
- `data/mock/` e `src/utils/`: diretórios regulares vazios antes dos testes e reconfirmados imediatamente antes de `rmdir`.

**Remoções efetivas:** exatamente os quatro arquivos A1 e os 25 A2 enumerados na seção 4, total **29/29 arquivos**, 424.498 bytes lógicos. **Preservados por risco não previsto: 0/29**; nenhum candidato apresentou dependência essencial adicional. Diretórios removidos: somente `data/mock/` e `src/utils/`. Foram usados `Path.unlink()` por caminho exato e `Path.rmdir()` após teste de vazio; sem recursão, `git clean`, `git reset`, commit ou push.

Único arquivo remanescente editado nesta execução: `docs/PENDING.md`, para registrar o resultado. `AGENTS.md`, `CURRENT_VERSION.md`, README e documentação das outras versões permaneceram intactos. Todos os 38 arquivos B e os 29 C foram explicitamente excluídos da lista de remoção e preservados por hash.

### Recuperação preparada

Antes de remover, foram copiadas e conferidas por SHA-256 as versões originais dos 29 arquivos e deste documento em `/tmp/managerai-clean-phase1-q5py625j/files/`, mantendo os caminhos relativos. Esse diretório também contém `baseline.json` (status/HEADs, lista, justificativas e hashes), `removal.json`, resultados de validação e logs transitórios. Não foi criado outro arquivo no projeto.

Rollback, se necessário: recuperar somente os caminhos removidos a partir de `files/`, conferir hashes contra `baseline.json`, recriar apenas os dois diretórios vazios e restaurar este documento anterior somente se for preciso reverter também o registro. Não aplicar reset/clean nem sobrescrever trabalho preexistente. **A cópia em `/tmp` é temporária e não substitui arquivo histórico durável**; não foi apagada nesta execução.

### Testes antes e depois

Mesmo Python 3.12.3 e ambiente existente, sem instalações. Comando da suíte em ambos os momentos:

```bash
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg venv/bin/python -B -m unittest discover -s tests -v
```

Para cada execução, `TMPDIR`, `MPLCONFIGDIR`, `XDG_CACHE_HOME` e `XDG_CONFIG_HOME` foram isolados em diretório temporário `/tmp/managerai-phase1-before-*` ou `/tmp/managerai-phase1-after-*`. Saída capturada em logs sob o diretório de recuperação, sem gerar saídas na EDA/brutos. Avisos conhecidos de AppTest `missing ScriptRunContext` não produziram falhas.

| Validação | Antes | Depois |
|---|---|---|
| Suíte completa, integração real e opcionais | 135 aprovados; 0 falhas, 0 erros, 0 pulos; 61,520 s | 135 aprovados; 0 falhas, 0 erros, 0 pulos; 61,015 s |
| Processo da suíte | Código 0 | Código 0 |
| Conferência independente de métricas | 16/16 aprovadas, código 0 | 16/16 aprovadas, código 0 |
| Sintaxe Python | 47 arquivos válidos | 46 arquivos válidos; diferença corresponde apenas a `src/extract.py` vazio removido |
| Links Markdown locais | 73 destinos, nenhum ausente, 62 documentos | 73 destinos, nenhum ausente, 61 documentos; saiu apenas o Markdown duplicado sem links |

Comando das comparações: `PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py`; oito métricas em dois jogos (3754320 e 3773585), catálogo de 26. O resultado posterior coincide com o anterior. A suíte completa inclui preservação byte a byte do baseline legado, schema V3 aditivo, exclusão temporal, mudanças de fonte/cobertura, referências de hipóteses, UI e figuras. Checagem estática adicional: 84 imports relativos em `src/managerai/`, nenhum destino ausente; ajuda CLI também executada com sucesso. Não houve teste manual de navegador nem validação esportiva.

### Integridade dos arquivos protegidos

Baseline SHA-256 inicial de **9.255 arquivos**: 275 do projeto (incluindo caches/EDA) e 8.980 do clone StatsBomb fora de seu `.git/`. Após remover A, os **9.226 arquivos restantes** foram comparados integralmente por hash, sem alteração ou acréscimo antes da edição deste registro. Isso inclui os **8.977 arquivos de `open-data/data/`**, os **108 arquivos da EDA**, fontes funcionais, testes, fixture congelada, exemplos mantidos, licenças, B/C e todos os demais documentos. Excluídos dessa varredura: ambientes virtuais, metadados Git e diretórios de configuração do ambiente; nenhum deles foi alvo de escrita pelo procedimento.

Fixture mantida: `outputs/mvp_demo_city_arsenal/report.json`, SHA-256 `424389e2af0afee96eff3d5a7ef79d74f914f12f0965a052d361fe657fd56b08`. HEAD StatsBomb preservado: `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`; `git -C open-data status --short` vazio antes/depois. Não houve alteração de dados, EDA, contratos ou lógica; após as conferências, apenas este registro documental foi atualizado. Os caches removidos não foram recriados.

`git status --short` final:

```text
 D outputs/meu_primeiro_teste/report.json
 D outputs/meu_primeiro_teste/report.md
 D src/.gitkeep
 D src/extract.py
?? AGENTS.md
?? docs/CURRENT_VERSION.md
?? docs/PENDING.md
?? docs/REPOSITORY_AUDIT.md
?? open-data/
```

As quatro exclusões rastreadas correspondem a A1. Os 25 caches ignorados e os dois diretórios vazios não aparecem no status; os cinco itens `??` já existiam no início, inclusive este documento, cuja edição não aparece como `M` por ainda não estar rastreado. `git diff --check` sem problemas. A Fase 1 está encerrada; próximas ações dos 38 condicionados são revisão da consolidação, autorização para migrar README/links, confirmação da configuração VSCode e transferência prévia dos PNGs históricos quando necessária, sempre com nova aprovação para a limpeza física.
