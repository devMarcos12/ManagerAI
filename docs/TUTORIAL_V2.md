                                      # ManagerAI V2 — interface, relatórios e testes

## 1. Iniciar a interface

Execute da raiz do repositório. O ambiente virtual `venv` existente já recebeu a
dependência de interface nesta entrega. Para reproduzir em outro ambiente Python
3.12+, instale o arquivo separado:

```bash
venv/bin/python -m pip install -r requirements-ui.txt
venv/bin/python -m streamlit run streamlit_app.py
```

Abra **http://localhost:8501** no navegador. Para parar o servidor, pressione
Ctrl+C no terminal em que ele foi iniciado. Se não houver ambiente virtual:

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements-ui.txt
```

Não execute novamente a criação do ambiente virtual se ele já existir. A instalação
requer acesso ao índice de pacotes; o funcionamento posterior utiliza somente os
dados locais. Não há LLM, chave de API, GPU ou serviço pago. O núcleo e a CLI
continuam funcionando sem Streamlit. A versão de interface validada é Streamlit
1.65.0, fixada em `requirements-ui.txt`.

O arquivo `.streamlit/config.toml` limita o servidor a localhost, desativa a abertura
automática de navegador e desativa estatísticas de uso. Para usar outra porta:

```bash
venv/bin/python -m streamlit run streamlit_app.py --server.port 8502
```

## 2. Reproduzir Manchester City × Arsenal por nome

1. Escolha **Premier League** e temporada **2015/2016**.
2. Em **Meu time**, selecione **Manchester City**; em **Adversário**, **Arsenal**.
3. Mantenha **Partida histórica** e escolha **08/05/2016 — Manchester City × Arsenal**.
4. Mantenha **10 jogos anteriores por equipe** e os campos manuais nos padrões.
5. Clique em **Analisar confronto** e aguarde o indicador de carregamento.
6. Leia o resumo, a comparação curta, os pontos de atenção e os ajustes condicionais.
7. Use os botões para baixar o relatório legível `.md` e o relatório técnico `.json`.

O seletor impede equipes iguais. A partida mostra data e mando formal; não revela
placar como evidência pré-jogo. Os valores observados no snapshot validado incluem:

| Indicador | Manchester City | Arsenal |
|---|---:|---:|
| Finalizações por jogo | 13,30 | 15,30 |
| Gols esperados a favor por jogo | 1,58 | 1,50 |
| Passes certos | 81,93% | 83,79% |
| Entradas no terço de ataque por 90 min | 59,90 | 63,54 |

Esses números são calculados dos JSONs, não fixados no aplicativo. Há cinco
observações no resumo e duas hipóteses condicionais nesse cenário. A janela de
Manchester City vai de 02/03/2016 a 01/05/2016; a do Arsenal, de 28/02/2016 a
30/04/2016. Cada equipe tem dez jogos. O alvo e o próprio dia do corte são excluídos.

**Gols esperados não são contagem de chances, gols reais nem probabilidade de vitória.**
As hipóteses indicam o que revisar/testar, com observações numéricas, riscos,
pré-condições e limites. Não representam uma tática ideal validada.

## 3. Informações manuais e campos que não estão disponíveis

Mando, contexto, objetivo e notas são declarações do treinador. Aparecem no
relatório, mas **não alteram os cálculos ou gatilhos**. O mando formal do calendário
é separado do mando declarado.

Não há seletor de atletas na UI: o estudo de elegibilidade/forma por jogador não
está concluído e não se sugerem escalações ou substitutos. A opção manual de
indisponibilidade já existente na CLI permanece disponível e validada pelo histórico.

## 4. Testar ausência de histórico e pouca amostra

**Sem histórico:** mantenha as equipes e temporada, escolha **Data de corte livre**,
informe **08/08/2015** e analise. Espere zero jogos, indicadores indisponíveis,
aviso de histórico insuficiente e nenhuma hipótese artificial.

**Janela pequena:** volte à partida de **08/05/2016**, escolha **2 jogos anteriores**
e analise. Os indicadores disponíveis continuam visíveis, mas o aviso informa a
limitação e nenhuma hipótese é emitida.

Ao mudar equipes, temporada, modo ou referência, o resultado anterior é removido.
Ao editar o formulário de janela/contexto, clique novamente em **Analisar confronto**:
o resultado e os downloads sempre identificam a última análise enviada. Trocar
campos e baixar arquivos não dispara leitura de eventos nem recalcula features.

Os relatórios desses casos estão preservados em:

- `outputs/v2_city_arsenal/`: cenário normal, JSON idêntico ao V1;
- `outputs/v2_sem_historico/`: zero jogos e nenhuma hipótese;
- `outputs/v2_amostra_pequena/`: dois jogos por equipe e nenhuma hipótese.

## 5. Conferir detalhes e rastreabilidade

Na tela, abra **Todos os indicadores e detalhes técnicos** para acessar o vocabulário
completo, a versão detalhada anterior e o JSON. O Markdown baixado inclui apêndice
técnico. O JSON mantém unidades internas, valores exatos, regras, referências,
numeradores, denominadores, medianas, dispersão, IDs das partidas e hashes das fontes.

Os números são arredondados somente para exibição, em formato brasileiro: vírgula
decimal e ponto para milhar. Indisponível não é convertido em zero e passes sem
informação de pressão não são rotulados como passes comprovadamente sem pressão.
Não são inferidos corredores esquerdo/direito a partir de orientação não validada.

## 6. Executar os testes

Testes do núcleo e de apresentação, sem instalar Streamlit:

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Os testes opcionais da UI serão pulados se Streamlit não estiver nesse Python.
Para executar **tudo**, incluindo interface e integração real:

```bash
MANAGERAI_RUN_LOCAL_TESTS=1 PYTHONPATH=src venv/bin/python -B -m unittest discover -s tests -v
```

Na entrega foram executados **48 testes, todos aprovados**, incluindo:

- testes anteriores de integridade, temporalidade e abstenção;
- vocabulário, formatação brasileira e ausência de códigos internos no corpo amigável;
- fidelidade de valores, evidências de cada hipótese e não alteração do relatório;
- igualdade exata do JSON real contra o artefato V1;
- AppTest do Streamlit: seleção por nome, impedimento de equipes iguais, nenhuma
  leitura de eventos antes do envio, estados de amostra, erros e limpeza de resultado;
- payloads e links de download, além de ausência de recálculo ao baixar;
- fluxo real City × Arsenal na UI com JSON idêntico à CLI e à V1.

Os testes de UI usam o [AppTest oficial](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
Simulam interações funcionais sem navegador; não substituem avaliação visual e
de usabilidade com a comissão técnica. Avisos `missing ScriptRunContext` emitidos
pelo executor de testes não são erros exibidos no aplicativo.

## 7. CLI preservada e comparação com a V1

Todos os comandos anteriores permanecem válidos. O Markdown agora é amigável com
apêndice técnico; o JSON não muda. Use sempre um diretório novo:

```bash
PYTHONPATH=src python3 -B -m managerai analyze \
  --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 \
  --target-match-id 3754314 --window 10 \
  --output-dir outputs/meu_relatorio_v2_01
cmp outputs/mvp_demo_city_arsenal/report.json outputs/meu_relatorio_v2_01/report.json
```

`cmp` deve terminar sem saída e com código 0 no snapshot atual, usando os mesmos
campos e contexto padrão. O contexto manual faz parte da requisição/JSON; mudar
notas ou objetivo altera esses campos, embora não altere os indicadores ou regras.

## 8. Dados em outra pasta e diagnóstico

A pasta é configuração administrativa, não entrada livre do treinador. Exemplo:

```bash
MANAGERAI_DATA_ROOT=/caminho/para/open-data/data venv/bin/python -m streamlit run streamlit_app.py
```

| Situação | Comportamento / ação |
|---|---|
| Dataset ausente ou sem acesso | Mensagem legível, sem traceback cru; confira a pasta administrativa |
| Confronto sem partida-alvo no recorte | Envio bloqueado nesse modo; use data livre |
| Partida incompatível com as equipes | Validação do pipeline impede análise |
| Indicador indisponível | Consulte amostra e denominador nos detalhes; não usar outra métrica como substituto implícito |
| Catálogo mudou em disco | Clique em Atualizar catálogo; metadados têm cache curto de 60 segundos |
| Alteração de campo não atualizou números | Envie novamente o formulário; confira a identificação da última análise |
| Saída da CLI já existe | Escolha outro nome; relatórios anteriores não são sobrescritos |

A UI mantém o resultado apenas na sessão e oferece downloads em memória; não
escreve relatórios em caminhos arbitrários. Reiniciar a sessão descarta esse resultado.
Eventos não ficam em cache entre análises: um novo envio lê os dados e renova seus
hashes. Só catálogo e calendário usam cache.
