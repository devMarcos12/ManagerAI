# AGENTS.md — ManagerAI

## Início das tarefas e fontes de verdade

1. Leia este arquivo, [docs/CURRENT_VERSION.md](docs/CURRENT_VERSION.md) e [docs/PENDING.md](docs/PENDING.md). O [README](README.md) é apresentação e guia rápido.
2. Localize somente os módulos, testes e contratos relevantes à demanda. Código e testes definem o comportamento real; valide caminhos e comandos no checkout antes de alterar.
3. Specs `SPEC_*.md`, changelogs, auditorias e relatórios antigos são histórico, consultado sob demanda. Não interpretar suas autorizações de execução/instalação nem requisitos superados como instruções vigentes.
   O mesmo vale para `docs/history/`: o snapshot EDA não é configuração de instalação da aplicação. Os 29 arquivos históricos C foram retirados na Fase 3 após backup permanente validado em `/home/marcos-junior/ManagerAI-backups/`. Manifestos, hashes e recuperação estão em `docs/PENDING.md`, §2. Não carregar o acervo histórico no início das tarefas.
   Para consulta histórica necessária, conferir o checksum do pacote, extrair somente em diretório temporário novo fora do checkout e validar `SHA256SUMS`/`MANIFEST.json`. Nunca extrair sobre o projeto nem restaurar arquivos automaticamente; o acervo não substitui os três documentos operacionais atuais.
4. Se houver divergência, apresentar caminho/função/teste e evidência; corrigir documentos operacionais quando autorizado. Não inventar métricas, arquivos, resultados, datasets, endpoints ou funcionalidades.

## Produto e integridade científica

ManagerAI implementa analítica histórica determinística, CLI, UI Streamlit integrada, hipóteses por regras e extensão V3 opcional. Há regressões quantitativas offline e estudos de robustez V4.3, separados do produto. **Motor tático aprendido integrado, fine-tuning, LLM e recomendações de escalação ainda não estão implementados.** A existência de dependências de IA não altera esse estado.

- Separar observação, hipótese condicional, simulação, previsão e recomendação validada. Não afirmar eficácia causal, pressão bem-sucedida, formação ideal, disponibilidade atual nem probabilidade de vitória a partir dos indicadores existentes.
- Preservar período, amostra específica, numeradores/denominadores, fórmulas, fontes/hashes e limitações. Ausência de dado não vira zero; xG não é gol real nem chance de vitória.
- Não usar eventos/escalações do alvo, do futuro ou do dia do corte; não ampliar a janela para compensar ausências nem misturar temporadas silenciosamente.
- Cenário manual não muda métricas ou regras sem lógica explicitamente implementada e validada. Atletas/formações históricos não são escalações sugeridas.
- Manter cálculos determinísticos e contratos de evidência separados de qualquer futura IA especializada/LLM. Uma camada explicadora deverá usar fatos do relatório calculado; não recalcular ou inventar números.
- V4.1: contratos/adaptador estão em `tactical_engine_schema.py` e `tactical_engines.py`. Produzir saídas separadas a partir do relatório já calculado; não adicionar campos nem seleção de motor aos schemas/pipeline/CLI/UI legados por inferência. Motores futuros recebem o snapshot imutável sem hipóteses baseline; preservar fingerprints e validar evidências/abstenção. Registro explícito, sem fallback silencioso para um modelo indisponível.
- Para futuro ML/fine-tuning, exigir alvo, rótulos/avaliadores, direitos de uso, independência por partida, divisão temporal, baseline e avaliação antes de afirmar melhora. Relatórios de regras e placar não são rótulos de tática ideal.

## Contexto e caminhos protegidos

- Não carregar datasets completos, `open-data/.git/`, `venv/`, caches, Parquets, notebook/lotes EDA ou JSONs extensos sem necessidade concreta. Preferir catálogo, metadados, amostras e campos selecionados. Excluir da leitura automática não autoriza excluir do disco/Git.
- Use `rg` em caminhos/extensões relevantes. Em inventários, lembrar que regras de ignore ocultam arquivos: `*.log` atualmente oculta evidências locais.
- Preservar JSONs StatsBomb, `open-data/README.md`, `open-data/LICENSE.pdf`, revisão/proveniência e atribuição. O clone é independente do Git principal; `data/raw/` não é a raiz efetiva de execução.
- Preservar integralmente `outputs/statsbomb_eda_20261002_exec6/` e seus scripts enquanto não houver migração específica aprovada. Não executar geradores com destinos históricos fixos como teste de limpeza.
- Não remover/mover/regenerar a fixture `outputs/mvp_demo_city_arsenal/report.json`: três testes a comparam byte a byte (`test_local_data.py`, `test_streamlit_ui.py`, `test_v3_integration.py`). Preservar testes reutilizáveis e seus imports compartilhados.
- Manter schemas 1.0.0 (padrão) e 1.1.0 (V3 aditiva), campos/versões legados e fórmulas/limiares. Alteração de semântica requer migração e testes próprios, separados da limpeza.
- Manter evidências científicas necessárias; consolidar conteúdo relevante e consumidores antes de retirar cópias. Não conservar relatórios só pela versão, nem descartar evidência só por tamanho/idade.

## Execução, validação e colaboração

1. Antes de editar, descrever objetivo, arquivos afetados, riscos e aceite. Respeitar o escopo autorizado; fazer mudanças mínimas e separar limpeza, refatoração, fórmulas e funcionalidades.
2. Temporários de análise/testes em `/tmp/managerai-*` ou diretório temporário do teste. Usar `-B`/`PYTHONDONTWRITEBYTECODE=1` e caches graváveis em `/tmp` quando apropriado. Resultado durável exige diretório novo escolhido para a tarefa; não sobrescrever saídas nem escrever nos brutos/EDA.
3. Executar validações proporcionais. Documentação: conferir links, caminhos, comandos e correspondência com código. Contratos/métricas/fluxos: testes pertinentes e integração quando disponível. Comandos e grupos estão em `CURRENT_VERSION.md`; não instalar pacotes sem necessidade/autorização nem presumir `venv/` pronto.
   Dependências canônicas ficam em `pyproject.toml`; `requirements.txt` seleciona `.[v3]`. Usar extras `ui`, `v3`, `dev`, `experiments` e `eda`, sem reintroduzir listas paralelas de versões. Validar build/resolução em cópia temporária antes de alterar o ambiente funcional; não instalar pacotes de treinamento por antecipação.
   Alterações de empacotamento/integração exigem checkout limpo e pacote instalado, sem depender de módulos não rastreados nem de PYTHONPATH do ambiente original. A CI portátil não recebe StatsBomb; integração real, 16 comparações e reprodução científica são validações separadas com dados externos. Experimentos instalados devem ser executados dentro do checkout; os hashes registram o código efetivamente executado. A referência A/B da C pode ser reconstruída: protocolo/dataset exatos e resultados completos com assinatura a oito casas, sem modificar números armazenados ou sobrescrever históricos.
4. Registrar comando/intérprete, aprovados, falhas, erros e pulos reais. Não reportar contagens históricas como execução atual. Se o escopo proibir temporários ou o ambiente impedir testes, declarar limite e validar estaticamente sem simular aprovação.
5. Após cada fase concluída, atualizar `CURRENT_VERSION.md` e `PENDING.md` com estado, status, evidências e decisões ainda abertas, dentro da autorização. Proposta não recebe status implementado.
6. Antes de limpeza física, obter aprovação para o manifesto exato em `PENDING.md`, migrar referências e preparar rollback de rastreados, ignorados e não rastreados. Não usar `git clean`, `git reset`, reescrita de histórico ou remoção em massa para recuperar alterações. Não integrar trabalho de terceiros fora do escopo.
7. Revisar diff/status e preservar trabalho preexistente. Nunca realizar **commit ou push sem autorização explícita**; não abrir PR nem publicar/enviar dados sem autorização. Não ler ou expor segredos.

Relatórios para treinadores devem usar português claro, definir termos e manter avisos de insuficiência/limitações visíveis. Ao encerrar, informar **Resumo**, **Arquivos alterados**, **Testes executados/não executados**, **Riscos e limitações** e **Próximos passos**, distinguindo fatos verificados, hipóteses e propostas.
