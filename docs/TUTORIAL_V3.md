# Tutorial — ManagerAI V2.2 e V3

Execute os comandos na pasta ManagerAI. O ambiente virtual `venv` existente já contém Streamlit e Matplotlib usados nesta entrega. Não é necessário cadastrar chave ou usar serviço externo.

## Abrir a interface

```bash
MPLCONFIGDIR=/tmp/managerai-mpl venv/bin/python -m streamlit run streamlit_app.py
```

Abra http://localhost:8501 no navegador. Para parar o servidor, pressione Ctrl+C no terminal que o iniciou. `MPLCONFIGDIR` apenas direciona o cache de gráficos para uma pasta gravável; não é pasta de dados.

Caso use um ambiente novo sem as dependências opcionais:

```bash
venv/bin/python -m pip install -r requirements-v3.txt
```

A instalação pode precisar de acesso ao repositório de pacotes; o funcionamento do sistema depois dela usa somente arquivos locais. O núcleo anterior continua sem essas dependências. Sem Matplotlib, a interface mantém a análise anterior e desabilita a opção V3 com uma explicação.

## Demonstrar City × Arsenal

1. Selecione Premier League, temporada 2015/2016, Manchester City e Arsenal.
2. Mantenha Partida histórica e selecione 08/05/2016. Escolha até 10 jogos anteriores por equipe.
3. Confira a prévia: dez jogos selecionados e com arquivos para cada equipe. Presença de arquivo não garante qualidade; esta é verificada ao analisar.
4. Marque **Incluir análise tática por eventos (V3)**. A opção começa desmarcada para preservar o comportamento anterior.
5. Se desejar, preencha o cenário declarado. Mando, contexto, objetivo e notas não modificam os indicadores ou gatilhos das hipóteses.
6. Clique em **Analisar confronto**. Leia amostra, períodos e avisos antes dos valores. Veja progressão, finalizações, pressão, sequências e participação histórica. Os dois gráficos estão na seção V3.
7. Baixe o relatório legível em Markdown e o JSON técnico. Downloads usam o resultado já calculado e não reexecutam o motor. Formações registradas não são sugestões; disponibilidade dos atletas no alvo continua desconhecida.

A V3 foi auditada integralmente para Premier League 2015/16 e La Liga 2020/21. Nas demais temporadas, a extensão fica desabilitada até nova auditoria de campos e orientação; a análise anterior continua disponível.

Sem marcar V3, o mesmo fluxo gera apresentação V2.2 e JSON original V1/V2. Mudar seleção, data, janela ou versão limpa o resultado; mudar campos do cenário só se aplica após novo envio, conforme a mensagem exibida.

## Demonstrar a limitação Real Madrid × Barcelona

Selecione La Liga, 2020/2021, Real Madrid e Barcelona, partida de 10/04/2021 e janela 10. A prévia avisa que existe apenas **um jogo anterior do Real Madrid**, enquanto o Barcelona tem dez selecionados. Execute para exploração descritiva. O relatório repete o alerta e mantém os números, mas não apresenta conclusões comparativas nem hipóteses. A janela não é completada com outros anos, partidas do alvo ou jogos futuros.

Para experimentar n=0, use Data de corte livre no começo da temporada; para n=1, escolha janela 1. Informação indisponível não é zero e uma única observação não recebe desvio-padrão.

## Gerar pelo terminal

Cada execução exige um diretório **novo**; escolha outro nome se já existir. Os comandos abaixo não alteram relatórios anteriores:

```bash
MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m managerai analyze --competition-id 2 --season-id 27 --team-id 36 --opponent-id 1 --target-match-id 3754314 --window 10 --v3 --output-dir outputs/minha_demonstracao_v3_city
MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m managerai analyze --competition-id 11 --season-id 90 --team-id 220 --opponent-id 217 --target-match-id 3773497 --window 10 --v3 --output-dir outputs/minha_demonstracao_v3_real
```

Abra `report.md`; as imagens `shot_map.png` e `progression_entries.png` ficam ao lado. `report.json` contém valores exatos, partidas, eventos, denominadores e hashes. Na resposta do terminal, `hypotheses` conta as regras anteriores e `v3_hypotheses` conta as novas. Nenhuma contagem representa probabilidade de sucesso.

Retire `--v3` para usar o contrato original. A API Python mantém `analyze(root, request)`; a extensão usa `analyze(root, request, include_v3=True)`. Para corte livre, substitua `--target-match-id` por `--cutoff-date AAAA-MM-DD`; os modos são exclusivos e todo o dia do corte fica excluído.

## Rodar os testes

Suíte completa, incluindo dados locais e interface:

```bash
MANAGERAI_RUN_LOCAL_TESTS=1 MPLCONFIGDIR=/tmp/managerai-mpl PYTHONPATH=src venv/bin/python -B -m unittest discover -s tests -v
venv/bin/python -m pip check
```

Sem `MANAGERAI_RUN_LOCAL_TESTS=1`, os casos reais são pulados explicitamente; fixtures sintéticas continuam verificando limites, nulos e temporalidade. Testes opcionais de interface/gráficos exigem suas dependências. Nenhum teste modifica o dataset: corrupção de alvo/futuro ocorre apenas em pastas temporárias sintéticas.

Para conferir as métricas diretamente nos JSONs originais:

```bash
PYTHONPATH=src venv/bin/python -B outputs/v22_v3_validation/check_metrics.py
```

O script imprime o resultado e não grava arquivos. Consulte [a conferência](V3_METRICS_CHECK.md), [o contrato V3](REPORT_SCHEMA_V3.md) e [o relatório de entrega](RELATORIO_FINAL_V2_2_V3.md).

## Ler com cuidado

xG estima a qualidade das finalizações; não é quantidade de chances nem chance de vitória. Pressão registrada não significa pressão bem-sucedida. Blocos de ações não equivalem a todas as posses reais. Cinco jogos é mínimo operacional, sem significância estatística garantida. As hipóteses precisam de vídeo, treino e revisão da comissão técnica.

A UI foi testada com Streamlit AppTest e as imagens exportadas foram inspecionadas. Isso não substitui revisão de navegação, acessibilidade e usabilidade em navegador por uma pessoa.
