# ManagerAI — pendências e execução das fases

Atualizado em 17/10/2026. Estado técnico e procedimentos: [CURRENT_VERSION.md](CURRENT_VERSION.md). Regras: [AGENTS.md](../AGENTS.md). **Fases 1–3 concluídas: dependências centralizadas, B1/B2/B3 consolidados e retirados; os 29 arquivos C foram removidos na Fase 3 após backup permanente validado.** B4 permanece por decisão humana. Histórico e recuperação: §5; validação desta execução: §8. Nenhuma funcionalidade foi alterada.

## 1. Prioridades e critérios de conclusão

| ID | Prioridade / status | Próxima ação, dependência e critério de conclusão |
|---|---|---|
| DOC-01 / DOC-02 | P0 / CONCLUÍDOS | Três documentos operacionais e README atualizados; dez documentos B1 revistos e informações essenciais migradas |
| ENV-01 | P1 / IMPLEMENTADO E VALIDADO LOCALMENTE | Pyproject canônico, requirements simples, extras opcionais e snapshot EDA preservado. Build/dry-runs offline passam; instalação limpa em outro ambiente e lock de transitivas ainda não verificados |
| CLEAN-01 / CLEAN-02 | P1 / A, B1–B3 E C CONCLUÍDOS | Fase 1: 29 arquivos e dois diretórios vazios. Fase 2: 37 B1–B3 e dois requirements paralelos. Fase 3: 29 C preservados externamente e removidos. B4 continua presente |
| HIST-01 | P0 / CONCLUÍDO LOCALMENTE | Destino permanente solicitado pelo responsável: `/home/marcos-junior/ManagerAI-backups/`. Dois pacotes preservados, manifestos/hashes/recuperação testados; 29/29 C removidos. Cópia externa redundante e acesso pela equipe não foram validados |
| B4 | P2 / DECISÃO HUMANA | Confirmar se `.vscode/settings.json` é pessoal ou compartilhado antes de retirar |
| VAL-02 | P0 / CONCLUÍDO NA FASE 2 | 135 testes e 16 comparações antes/depois; build, extras, CLI, imports, JSON e links verificados; integridade protegida conferida |
| VAL-03 | P0 / CONCLUÍDO NA FASE 3 | Resultados atuais de testes, 16 comparações, contratos, links e hashes registrados no §8 |
| DATA-01 | P1 / DECISÃO HUMANA | Provisionamento do clone externo: revisão fixa, licença, responsável e recuperação por outro integrante; não mover dados/EDA |
| ART-01 | P1 / PENDENTE | Política explícita para novas saídas e logs científicos no `.gitignore`, preservando fixtures/evidências; não ignorar outputs inteiro |
| TEAM-01 | P2 / DECISÃO HUMANA | Definir responsáveis por contratos, indicadores/dados, UI e avaliação; revisar os documentos locais ainda não rastreados |
| REF-01 | P2 / NÃO INICIADO | Consolidar constantes de suficiência e revisar acoplamento de regras/apresentação em refatoração separada, com os mesmos contratos/fórmulas |
| V3-01 | P2 / NÃO INICIADO | Auditar campos/orientação de novas temporadas e envelhecimento da evidência antes de alterar VALIDATED_RECUTS |
| PERF-01 | P2 / NÃO INICIADO | Medir tamanho do JSON e custo de releitura sem retirar proveniência ou alterar schema silenciosamente |
| EVAL-01 | P1 / NÃO INICIADO | Aplicar avaliação de correção, rastreabilidade, compreensão, plausibilidade, condições/riscos e utilidade com especialistas/vídeo/treino |
| AI-01 | P3 / PLANEJADO, NÃO IMPLEMENTADO | Definir tarefa e avaliação do motor/modelo especializado, mantendo baseline determinístico |
| AI-02 | P3 / PLANEJADO, NÃO IMPLEMENTADO | Fine-tuning depende de alvo, rótulos, avaliadores/concordância, direitos e split temporal; nenhum pacote/modelo escolhido |
| AI-03 | P3 / PLANEJADO, NÃO IMPLEMENTADO | LLM explicadora depende de provedor/custo e avaliação de fidelidade; números continuam vindo do relatório calculado |
| AI-04 | P3 / NÃO IMPLEMENTADO, SEM ESCOPO APROVADO | Escalação/formação ideal exige tarefa, disponibilidade e validação próprias; atletas históricos não bastam |

Não há treinamento, fine-tuning, modelo especializado, integração LLM ou recomendação de escalação implementados. `PENDENTE` não autoriza trabalho; a integração da UI ao núcleo já existe.

## 2. Dependências implementadas

- `pyproject.toml` é canônico. Núcleo: `dependencies=[]`. Extras `ui` (Streamlit 1.65.0), `v3` e `dev` (Streamlit 1.65.0 + Matplotlib 3.11.2), `eda` (pandas/numpy/pyarrow/matplotlib/seaborn/nbformat/Pillow). Os pins diretos correspondem aos pacotes já disponíveis; não houve atualização/removal de bibliotecas do venv.
- `requirements.txt` seleciona `.[v3]` a partir da raiz. Os dois requirements antigos saíram somente depois de migrar README, estado atual, diagnóstico CLI e mensagens de testes. Referências em specs/auditorias datadas são registros históricos, sem autoridade de instalação atual.
- O snapshot original de 158 linhas ficou byte a byte em `docs/history/requirements-eda-20261017.txt`, SHA-256 `cda85b3a30d5094ec44bc285b580cecb195047f9fa7ff43bee6994a811e9453b`, e também no pacote externo. Não é requisito operacional e não deve ser instalado para rodar a aplicação.
- Não se criou extra de fine-tuning vazio ou com bibliotecas presumidas: tarefa/modelo e dependências ainda não definidos. Qualquer grupo futuro deverá ser opcional e isolado. O extra `dev` usa somente os opcionais que a suíte atual realmente requer; `unittest` é padrão.
- Build usa setuptools existente (84.0.0); a distribuição `wheel` separada não estava instalada e não precisou ser instalada. Não há lock de transitivas nem alegação de instalação limpa/remota validada.

## 3. Consolidação técnica de B1

Revisão integral dos dez documentos, confrontada com o código e testes existentes. A consolidação já tinha as fórmulas/IDs/contratos; a Fase 2 acrescentou campos/tipos de dados, contadores históricos contextualizados, semântica de metadados/comparação, efeitos do cenário no JSON, diagnóstico/cache da UI e detalhes do protocolo de avaliação. Não copiaram-se previsões obsoletas de contagem de pulos nem o formulário não reativo do tutorial V2.

| Documento retirado | Conteúdo vigente em CURRENT_VERSION.md |
|---|---|
| `docs/architecture.md` | §§2 e 5: fluxo, módulos, entrada/saída e compatibilidade |
| `docs/data_dictionary.md` | §3: fonte, campos/tipos, cobertura, qualidade e temporalidade; detalhes históricos mantidos no C |
| `docs/metrics.md` | §4: 21 IDs, fórmulas, nulos e diferenças em relação à EDA |
| `docs/tactical_rules.md` | §4: R01/R02/R03, limiar e pré-condições |
| `docs/evaluation.md` | §7: baseline, avaliação humana, independência por jogo e separação temporal |
| `docs/AVALIACAO_COMISSAO_TECNICA.md` | §7: identificação, classificação da revisão, vídeo/treino, utilidade e desacordos |
| `docs/REPORT_SCHEMA_V3.md` | §§4 e 5: 26 IDs, sequências/histórico, regras e contrato aditivo |
| `docs/TUTORIAL_TESTES.md` | §§6 e 7: CLI, cortes, cenários, erros, reprodução e suíte |
| `docs/TUTORIAL_V2.md` | §§1, 2, 6 e 7: UI integrada, cenário manual, cache/downloads e diagnóstico |
| `docs/TUTORIAL_V3.md` | §§3, 6 e 7: recortes, comandos, demos, figuras e validação |

Na Fase 2, os três documentos C com links para B1 tiveram **somente destinos de navegação migrados**: `CHANGELOG_V2.md`, `docs/RELATORIO_FINAL_V2_2_V3.md`, `docs/V3_DATA_FEASIBILITY.md`. Nenhum resultado, número, limitação ou comando histórico foi reescrito. Suas versões anteriores à migração estão no arquivo verificado. Os demais 26 C conservaram os mesmos bytes na Fase 2. Todos os estados foram preservados nos pacotes permanentes antes da retirada na Fase 3. O README operacional aponta exclusivamente para estado/pendências e os dois exemplos finais; nenhum link operacional exige B1/B2/B3.

## 4. Manifesto efetivamente executado e preservação

### Retirados nesta Fase 2 — 39 arquivos

São dez B1, 19 B2, oito B3 e dois arquivos paralelos de dependências, todos conferidos contra backup/hash antes de `unlink` por caminho exato. As listas originais e os registros detalhados da Fase 1 estão preservados no snapshot de PENDING anterior à Fase 2, no pacote externo. Não houve exclusão recursiva, reset, clean, commit ou push.

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
outputs/v3_city_arsenal/README.md
outputs/v3_city_arsenal/report.json
outputs/v3_city_arsenal/report.md
outputs/v3_city_arsenal/shot_map.png
outputs/v3_real_madrid_barcelona/README.md
outputs/v3_real_madrid_barcelona/report.json
outputs/v3_real_madrid_barcelona/report.md
outputs/v3_real_madrid_barcelona/shot_map.png
requirements-ui.txt
requirements-v3.txt
```

B2: casos normal, data livre, primeira data e janela pequena estão documentados/testados, sem exigir cada saída antiga. B3: JSON/Markdown/mapas iniciais eram idênticos aos finais; os gráficos de progressão únicos (C3) foram mantidos na Fase 2 e retirados somente na Fase 3, após preservação permanente comprovada. A correção da escala cortada está registrada e coberta por teste; não se preservaram cópias apenas por versão. Nenhum diretório adicional foi removido nesta fase.

### Preservados

- B4: `.vscode/settings.json`, sem decisão da equipe sobre uso compartilhado.
- Fixture: `outputs/mvp_demo_city_arsenal/report.json`, SHA-256 `424389e2af0afee96eff3d5a7ef79d74f914f12f0965a052d361fe657fd56b08`, ainda consumida por três testes.
- Exemplos finais: `outputs/v3_demo_city_arsenal/` e `outputs/v3_demo_real_madrid_barcelona/`, cada um com JSON/Markdown e dois PNGs; mesmos bytes, incluindo reprodução dos JSONs pela CLI.
- Verificadores/resultados: `outputs/v3_feasibility/` e `outputs/v22_v3_validation/{check_metrics.py,independent_metrics.json,final_summary.json}`; caminhos mantidos.
- Todos os 26 módulos Python ativos, entrada Streamlit, 14 módulos de testes, scripts EDA, dados/EDA originais, licença, venv e configurações fora do escopo.
### Grupo C — manifesto executado na Fase 3: 29 removidos

Os 29 caminhos abaixo foram conferidos individualmente e coincidem exatamente com o manifesto do pacote da Fase 2. Nenhum consumidor Python ativo foi encontrado; as referências operacionais já haviam sido migradas. Foram removidos somente após conferir os hashes dos originais com o snapshot atual, copiar os dois pacotes para o destino permanente aprovado e testar a recuperação. Inclui nove documentos, 18 evidências de execução (oito logs ignorados pelo Git) e dois PNGs históricos. Nenhum diretório foi removido. Arquivos preservados por risco: zero.

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
outputs/v3_city_arsenal/progression_entries.png
outputs/v3_real_madrid_barcelona/progression_entries.png
```

### Estado das fases anteriores

Consolidação: 135 aprovados, zero pulos (60,536 s); modo sem opcionais 110 aprovados/25 pulados; 16 comparações. Fase 1: 29/29 removidos, nenhum preservado por risco adicional, `data/mock/` e `src/utils/` vazios removidos; testes 135/135 antes (61,520 s) e depois (61,015 s), zero falhas/erros/pulos e 16/16 comparações em ambos. Foram preservados brutos, EDA, fixture e lógica. Detalhamento original da Fase 1, hashes/listas e status estão no snapshot `snapshots/PENDING-before-phase2.md` do pacote histórico. A cópia temporária de recuperação da Fase 1 foi `/tmp/managerai-clean-phase1-q5py625j/`.

## 5. Arquivo histórico e recuperação

Pacote original da Fase 2, cuja cópia temporária continua preservada (registro histórico):

```text
/tmp/managerai-phase2-x43whygj/ManagerAI-history-13c50e5-20261017.tar.gz
```

SHA-256 do pacote: `48a57a602895eba21526ead7a53495520263989881aa19cdfaa082d3de9cf236`; tamanho 253866 bytes. Commit de referência `13c50e5cc7e54e6f45487b89cdbe3994d621587f`, snapshot do início da Fase 2 com status local registrado. Os arquivos não rastreados/ignorados foram incluídos pelos bytes locais, não presumidos pelo commit.

Conteúdo: os **29 C com caminhos originais**, dois snapshots adicionais (`snapshots/requirements-eda-original.txt` e `snapshots/PENDING-before-phase2.md`), `MANIFEST.json`, `SHA256SUMS` e `RECOVERY.md`. O pacote foi extraído em diretório temporário vazio e todos os hashes conferidos; não inclui dataset/EDA completa nem venv. O SHA256SUMS também cobre o manifesto e instruções. Na Fase 2, `/tmp` não foi tratado como armazenamento definitivo. Na Fase 3, o responsável solicitou explicitamente `~/ManagerAI-backups/`; a cópia permanente foi concluída e validada antes de retirar qualquer original C.

Recuperação: conferir hash do `.tar.gz`, extrair em **diretório vazio fora do checkout**, executar `sha256sum -c SHA256SUMS` e conferir MANIFEST/commit. Restaurar seletivamente, verificando diferenças/consumidores, sem reset/clean nem sobrescrever trabalho alheio. Na Fase 3 os originais C foram retirados do checkout; a recuperação exata do estado anterior à retirada usa o pacote complementar da Fase 3 abaixo. Não substituir os dados originais por estes documentos nem instalar o snapshot EDA como requisito atual.

### Backup permanente validado na Fase 3

Diretório fora do repositório: `/home/marcos-junior/ManagerAI-backups/`, escolhido pelo responsável nesta tarefa. Contém os dois pacotes e seus arquivos laterais `.sha256`:

| Pacote | SHA-256 | Bytes / conteúdo validado |
|---|---|---|
| `ManagerAI-history-13c50e5-20261017.tar.gz` | `48a57a602895eba21526ead7a53495520263989881aa19cdfaa082d3de9cf236` | 253866; 29 C pré-migração + dois snapshots; 33 checksums internos |
| `ManagerAI-history-phase3-13c50e5-20261017.tar.gz` | `8930e55539ed6510ecb43a6e73ae6db02086086609bfcb7c203886ce50e9efd1` | 242030; exatamente os 29 C antes da retirada; 31 checksums internos |

Ambos preservam caminhos relativos, `MANIFEST.json`, `SHA256SUMS`, `RECOVERY.md` e referência ao commit `13c50e5cc7e54e6f45487b89cdbe3994d621587f`, com status local registrado. O manifesto da Fase 2 mantém seus metadados originais, inclusive o destino ainda pendente naquela data; a validação permanente ocorreu agora. O pacote complementar é necessário porque os três documentos com links migrados diferem do snapshot inicial da Fase 2. A diferença foi conferida removendo os destinos de links do texto: nenhum outro conteúdo difere. Os hashes de todos os 29 arquivos atuais coincidiram com o pacote complementar antes de cada exclusão; os dois pacotes originais em `/tmp` também foram preservados.

Validação de cada cópia permanente: SHA-256 integral; lista C exata (29 únicos); todos os membros regulares, relativos e sem `..` ou links; extração em diretório temporário exclusivo com criação sem sobrescrita; tamanhos/hashes do manifesto; `sha256sum -c SHA256SUMS` (33/33 e 31/31); instruções de recuperação presentes. Nenhuma extração foi feita sobre o checkout.

Para recuperar o estado imediatamente anterior à retirada:

```bash
cd /home/marcos-junior/ManagerAI-backups
sha256sum -c ManagerAI-history-phase3-13c50e5-20261017.tar.gz.sha256
mktemp -d /tmp/managerai-recovery-XXXXXXXX
# Use abaixo a pasta NOVA devolvida pelo comando anterior.
tar --keep-old-files --no-same-owner -xzf /home/marcos-junior/ManagerAI-backups/ManagerAI-history-phase3-13c50e5-20261017.tar.gz -C /pasta/nova
cd /pasta/nova
sha256sum -c SHA256SUMS
```

Confira `MANIFEST.json` e `RECOVERY.md`, compare com o checkout e restaure seletivamente somente os caminhos autorizados, sem sobrescrever trabalho existente. Para versões anteriores à migração de links e os snapshots EDA/PENDING, repita o procedimento com o pacote original da Fase 2, em outra pasta nova. Não executar instruções históricas automaticamente. O backup permanente local não equivale a redundância fora da máquina nem garante acesso pela equipe; isso continua decisão de armazenamento, sem impedir a limpeza expressamente autorizada nesta fase.

Rollback da Fase 2: `/tmp/managerai-phase2-x43whygj/backup/` contém pré-imagens dos arquivos editados/retirados com caminhos relativos; `baseline.json` contém hashes e status inicial; `removed.json` registra as 39 exclusões. Restaurar somente os caminhos da fase a partir dessas cópias, conferir hashes e repetir validação. Cópias em `/tmp` são temporárias, não backup durável aprovado.

## 6. Validação real da Fase 2

Python 3.12.3, Streamlit 1.65.0 e Matplotlib 3.11.2 existentes. Logs, builds, relatórios novos e caches somente em `/tmp/managerai-phase2-x43whygj/` ou temporários filhos. Avisos AppTest `missing ScriptRunContext` sem falhas. Não houve instalação/removal de pacotes do ambiente funcional, validação esportiva ou teste manual de navegador.

```bash
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg venv/bin/python -B -m unittest discover -s tests -v
PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py
```

Em cada suíte, `TMPDIR`, `MPLCONFIGDIR`, `XDG_CACHE_HOME` e `XDG_CONFIG_HOME` apontaram para temporários. Os comandos foram executados antes/depois das alterações estruturais/diagnósticas; a edição final deste registro não muda execução.

| Validação | Antes | Depois |
|---|---|---|
| Suíte completa real/UI/V3 | 135 aprovados; 0 falhas, 0 erros, 0 pulos; 60,763 s | 135 aprovados; 0 falhas, 0 erros, 0 pulos; 61,324 s |
| Conferência independente | 16/16, código 0 | 16/16, código 0; mesmos resultados |
| Código de saída da suíte | 0 | 0 |

Verificações adicionais:

- Wheel criado offline com `pip wheel --no-deps --no-index --no-build-isolation --no-cache-dir`, **em cópia temporária do projeto**, sem egg-info/build no checkout.
- `pip install --dry-run --no-index --no-build-isolation --no-cache-dir -r requirements.txt` e equivalente `.[ui,v3,dev,eda]`, também na cópia, passaram usando pacotes existentes. Nenhuma instalação foi realizada; isso não prova obtenção dos pacotes em ambiente limpo/remoto.
- `venv/bin/python -B -m pip check`: código 0, `No broken requirements found.`
- Wheel extraído/importado fora de `src/`, sem instalação: catálogo de 20 equipes com `--data-root` explícito. Documentação não promete dataset empacotado nem default portátil fora do checkout.
- CLI legado City reproduziu a fixture byte a byte. City e Real V3 reproduziram os JSONs finais, duas figuras cada, schema 1.1.0, amostras 10/10 e 1/10, duas/zero hipóteses V3. Saídas somente em `/tmp`.
- Streamlit validado pelo AppTest completo (seleção, cobertura, janela reativa, envio, figuras, downloads e estados de abstenção). Não foi necessário iniciar servidor de rede ou navegador.
- AST dos 46 arquivos Python válida. Estrutura dos três arquivos Python editados permaneceu igual após normalizar literais: só mudou diagnóstico da CLI e duas mensagens de pulo para indicar extras; nenhum teste/assertiva ou cálculo foi removido/alterado.
- Links Markdown locais: 39 destinos verificados após migrar consumidores, nenhum ausente. Referências textuais históricas aos caminhos antigos são registros, não links operacionais.
- Contratos 1.0.0/1.1.0, 21/26 métricas e fixture protegidos pela suíte e reprodução; a conferência final de hashes compara integralmente brutos, EDA e artefatos mantidos com o baseline desta fase.

Integridade final: 9.226 arquivos no baseline da Fase 2 e 9.188 remanescentes após 39 remoções e um snapshot acrescentado. Comparação SHA-256 integral confirmou 8.977 arquivos brutos e 108 EDA inalterados; fixture, demos finais, licenças e todos os cálculos mantidos. O clone permanece limpo e na revisão `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`. Dos 208 arquivos remanescentes do projeto fora do clone, somente os 12 editados abaixo diferem do baseline; há um arquivo novo e nenhuma outra remoção. O pacote histórico passou também pelo `sha256sum -c` dos 33 itens cobertos (payloads, manifesto e instruções).

Arquivos editados nesta fase:

```text
AGENTS.md
README.md
pyproject.toml
requirements.txt
docs/CURRENT_VERSION.md
docs/PENDING.md
CHANGELOG_V2.md
docs/RELATORIO_FINAL_V2_2_V3.md
docs/V3_DATA_FEASIBILITY.md
src/managerai/cli.py
tests/test_streamlit_ui.py
tests/test_v3_integration.py
```

Novo arquivo: `docs/history/requirements-eda-20261017.txt`. Os três C editados mudaram exclusivamente destinos de links (comparação do texto sem os destinos idêntica). Os três Python editados mudaram apenas mensagens; os demais fontes/testes têm o mesmo hash.

HEAD inicial/final `13c50e5cc7e54e6f45487b89cdbe3994d621587f`. O estado inicial já continha as quatro exclusões rastreadas da Fase 1 e cinco itens não rastreados (AGENTS, CURRENT_VERSION, PENDING, auditoria e clone externo). `git status --short` final: nove entradas ` M`, 43 entradas ` D` (39 desta fase e quatro preexistentes) e seis `??` (os cinco preexistentes e `docs/history/`). O status completo e a comparação por caminho estão em `/tmp/managerai-phase2-x43whygj/final_project.json`. `git diff --check` sem problemas. Não houve commit, push ou mudança de histórico.

## 7. Decisões ainda abertas

1. Definir redundância fora da máquina e acesso da equipe ao backup permanente local já validado. A retirada dos 29 C está concluída; não executar outras pendências nem novos descartes automaticamente.
2. Confirmar papel de `.vscode/settings.json` (B4), provisionamento dos dados e responsáveis de revisão. Não inferir essas decisões de uma lista de limpeza.
3. Decidir lock/transitivas e testar instalação limpa em outro ambiente, sem atualizar/remover pacotes do venv atual automaticamente.
4. Tratar `.gitignore` e saídas locais numa etapa própria, mantendo evidências científicas, fixtures, licenças e EDA.
5. Definir tarefa/rótulos/avaliação antes de modelos/fine-tuning/LLM/escalação. Não iniciar implementação como parte desta limpeza.

## 8. Validação real da Fase 3 — 17/10/2026

Escopo concluído: 29/29 C removidos por caminho exato, zero preservados por risco adicional e nenhum diretório retirado. Antes da remoção, os pacotes permanentes passaram por todas as verificações do §5. Não houve exclusão antes do aceite integral do backup. O manifesto executado permanece no §4; não foi iniciada outra pendência.

Arquivos editados nesta fase: somente `AGENTS.md`, `docs/CURRENT_VERSION.md` e `docs/PENDING.md`. README já apontava aos documentos operacionais/demos finais e não exigiu alteração. Nenhum arquivo foi criado na árvore do projeto. Alterações anteriores da Fase 2 foram preservadas; o status não corresponde somente a esta execução.

| Verificação executada após a retirada | Resultado real |
|---|---|
| Suíte completa com dados reais, UI e V3 | **135/135 aprovados**, zero falhas, erros e pulos; código 0; 75,726 s |
| Comparações independentes | **16/16 aprovadas**, código 0; JSON de resultados idêntico ao da Fase 2 |
| Contratos JSON | Fixture schema 1.0.0 e dois exemplos finais schema 1.1.0; campos dataclass, extensão aditiva `tactical_v3`, 21/26 indicadores e arrays de escalação/formação vazios conferidos; JSON sem NaN/Infinity |
| Imports e sintaxe | 46 arquivos Python com AST válida; 84 imports relativos resolvidos; 25 módulos importáveis carregados no venv existente; `__main__` validado por `python -B -S -m managerai --help`, código 0 |
| Links Markdown locais | 16 destinos existentes nos documentos remanescentes da raiz, `docs/` e `outputs/`; zero links quebrados. Clone do fornecedor não reescrito |
| Integridade SHA-256 | Baseline 9.188 arquivos; 9.159 remanescentes. Exatamente os 29 C ausentes, nenhum arquivo novo e somente os três documentos operacionais editados |
| Brutos e EDA | 8.977 arquivos em `open-data/data/` e 108 arquivos EDA com os mesmos hashes; licença, atribuição, scripts, testes, demos finais e código funcional inalterados |
| Fixture congelada | Mesmo SHA-256 `424389e2af0afee96eff3d5a7ef79d74f914f12f0965a052d361fe657fd56b08`; mantida no caminho consumido pelos três testes |
| Revisões Git | HEAD principal `13c50e5cc7e54e6f45487b89cdbe3994d621587f` inalterado; clone StatsBomb limpo e na revisão `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb` |

Comandos de testes: os mesmos do §6, com `MANAGERAI_RUN_LOCAL_TESTS=1`, `PYTHONPATH=src`, `PYTHONDONTWRITEBYTECODE=1`, `MPLBACKEND=Agg`, intérprete `venv/bin/python -B`, e `TMPDIR`/caches XDG/Matplotlib em temporários. Python 3.12.3; opcionais do ambiente existente, sem instalações. CLI/Streamlit e preservação byte a byte são cobertos pela suíte completa; nenhum servidor/navegador manual foi iniciado. Avisos AppTest `missing ScriptRunContext` e imports Streamlit sem runtime não causaram falhas. A suíte completa foi executada após a retirada nesta fase; resultados antes/depois da Fase 2 permanecem identificados no §6, sem serem apresentados como nova execução.

Logs e evidências transitórias desta fase em `/tmp/managerai-phase3-5g2mo6j1/`: `state.json` (status inicial e hashes dos 29 C), `before_hashes.json`, `after_hashes.json`, `reference_check.json`, `removed.json`, `permanent_validation.json`, `after_tests.log`, `after_summary.json`, `after_metrics.json`, `integrity.json` e `final_git_status.txt`. Pré-imagens dos três documentos em `preimages/`; arquivos históricos recuperáveis pelo backup permanente, independentemente de `/tmp`.

`git status --short`: inicial com nove ` M`, 43 ` D` e seis `??`; final com seis ` M`, 63 ` D` e cinco `??`. Das 29 retiradas desta fase, 20 são rastreadas, oito são logs ignorados e uma é a auditoria não rastreada. Três documentos C antes modificados agora aparecem como excluídos; nenhuma alteração funcional nova. `git diff --check` sem erros. Não houve commit, push, reset, clean ou modificação de histórico.

Raiz final (incluindo diretórios locais protegidos, que não foram limpos):

```text
ManagerAI/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── streamlit_app.py
├── .gitignore
├── .streamlit/
├── .vscode/
├── data/
├── docs/                       # CURRENT_VERSION.md, PENDING.md, history/
├── src/
├── tests/
├── scripts/
├── outputs/                    # fixture, demos finais, verificadores e EDA preservados
├── open-data/                  # clone externo original
├── venv/                       # ambiente funcional preservado
└── .git/, .agents/, .aws/, .codex/
```

Rollback da Fase 3: validar e extrair o pacote complementar conforme §5, comparar os 29 arquivos e restaurá-los seletivamente se autorizado; as pré-imagens dos três documentos permitem reverter somente a edição documental desta fase. Nunca extrair sobre o checkout nem restaurar todo o repositório por comando destrutivo. O backup permanente é local; redundância e compartilhamento exigem decisão futura. A Fase 3 termina aqui.
