# ManagerAI V2 — relatório para a comissão técnica e interface local

Implementação validada em 11/10/2026. Nenhum commit criado. Dados brutos e relatórios
anteriores preservados. Sem fine-tuning, predição de vitória, LLM ou recomendação nominal
de escalação/formação.

## O que mudou

- `presentation/terminology.py`: títulos, unidades e explicações dos 21 indicadores;
  números em pt-BR, valores ausentes explícitos e cautelas para gols esperados,
  pressão, desarmes e faixas espaciais.
- `presentation/coach_report.py`: visão geral, até cinco observações concretas,
  oito indicadores priorizados, atenção ao adversário e ajustes com observações
  numéricas, justificativa, ação a testar, condição, riscos e limites. Só usa valores
  calculados; cada hipótese acessa as suas próprias referências de evidência.
- `report_renderer.py`: `render_markdown` entrega a apresentação V2 com apêndice
  técnico. `render_technical_markdown` preserva a apresentação detalhada V1.
- `streamlit_app.py`, `streamlit_ui.py`, `ui_support.py`: seleção por nomes,
  referência histórica/data livre, cenário manual, carregamento, erros compreensíveis,
  detalhes avançados e downloads Markdown/JSON. Pipeline chamado diretamente.
- `requirements-ui.txt`: Streamlit 1.65.0 separado das dependências do núcleo.
  `.streamlit/config.toml`: servidor localhost e estatísticas de uso desativadas.
- `tests/test_presentation.py`, `tests/test_streamlit_ui.py` e extensão de
  `tests/test_local_data.py`: linguagem, valores, não mutação, regressão V1, fluxos
  UI e payloads de download. `README.md`, tutorial V2 e notas nos documentos originais.

## Preservação e decisões

O motor analítico, as fórmulas, as regras R01/R02/R03, o corte temporal e o contrato
`AnalysisReport` não foram alterados. `schema_version`, versões de fórmulas/regras e
versão do núcleo continuam iguais. A apresentação é identificada separadamente
como 2.0.0. Não há migração de schema nem recálculo na camada de apresentação.

O JSON do novo cenário normal é **idêntico byte a byte** ao artefato V1, inclusive
valores por partida, hashes, amostras e hipóteses. O Markdown difere na linguagem
e organização; a apresentação original permanece no apêndice.

Metadados têm cache de 60 segundos; eventos só são lidos após envio. Resultados
ficam na sessão, não em cache global de análises. Alterar a seleção principal limpa
o resultado; editar o formulário exige novo envio, explicitado na tela. Downloads
não disparam análise nem escrevem em disco no servidor.

Não há seletor de atletas na interface: evitaria transmitir uma elegibilidade ainda
não demonstrada. O contexto manual é exibido como cenário e não muda cálculos ou
gatilhos. Números arredondados nunca substituem os valores internos.

## Verificação executada

1. Antes das alterações: 30 testes descobertos, 29 aprovados e uma integração opt-in
   pulada. O Streamlit ainda não estava instalado.
2. Após implementação, comando completo:

   ```bash
   MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src venv/bin/python -B -m unittest discover -s tests -v
   ```

   **48 testes aprovados**, incluindo integrações reais CLI/pipeline e UI.
   Log: `outputs/v2_validation/tests.log`.
3. CLI antiga gerou novos relatórios para os cenários A, B e C. Comparação:

   ```bash
   cmp outputs/mvp_demo_city_arsenal/report.json outputs/v2_city_arsenal/report.json
   ```

   Código 0, sem diferenças. Nenhum artefato anterior sobrescrito.
4. AppTest validou nomes, equipes distintas, corte livre, janela pequena, erros,
   downloads, ausência de leitura antes de analisar e igualdade UI/V1. Os payloads
   de download foram conferidos contra o relatório calculado.
5. O servidor Streamlit iniciou em `127.0.0.1:8502`. Não foi realizada avaliação
   visual manual em navegador nem avaliação de usabilidade com treinadores.

## Demonstrações entregues

| Cenário | Arquivos | Resultado |
|---|---|---|
| City × Arsenal, 08/05/2016, janela 10 | `outputs/v2_city_arsenal/report.md` e `.json` | 10 jogos por equipe, cinco observações no resumo, quatro achados internos e duas hipóteses |
| Corte 08/08/2015 | `outputs/v2_sem_historico/report.md` e `.json` | Zero jogos; indicadores indisponíveis e nenhuma hipótese |
| Mesmo alvo, janela 2 | `outputs/v2_amostra_pequena/report.md` e `.json` | Dois jogos por equipe; ressalva de amostra e nenhuma hipótese |

Para executar a interface: `venv/bin/python -m streamlit run streamlit_app.py`.
Instruções completas: [docs/TUTORIAL_V2.md](docs/TUTORIAL_V2.md).

## Questões priorizadas para a próxima versão — somente planejamento

1. **Validação com a comissão técnica:** testar compreensão, utilidade e riscos das
   hipóteses; criar rubrica de avaliação e revisar limiares exploratórios com especialistas.
2. **Elenco e formações históricas:** estudar posições, minutos, vínculo por período,
   disponibilidade informada antes do jogo e cobertura. Definir elegibilidade antes
   de mostrar qualquer sugestão nominal ou formação condicional.
3. **Contexto real:** definir quais entradas podem mudar a análise, como representar
   seus efeitos e quais evidências seriam necessárias; não presumir causalidade de
   clássico, importância, mando ou objetivo.
4. **Semântica espacial:** verificar orientação, definições de zonas e cobertura
   antes de rotular lados ou desenhar mapas táticos para decisão.
5. **Modelagem preditiva:** definir tarefa-alvo, rótulos defensáveis, independência dos
   exemplos, baseline e avaliação temporal. Placar não é rótulo de estratégia ideal.
6. **LLM opcional:** só para apresentação, com referências obrigatórias e avaliação
   de fidelidade; nunca como fonte de números, atletas ou recomendações sem suporte.

Esses itens não foram implementados. A V2 continua histórica e descritiva, com
evidência limitada e abstenção quando não há suporte.
