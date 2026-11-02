# Observatório de custos de seguro

Aplicação Streamlit construída a partir da [EDA original](notebooks/eda-original.ipynb) de Galileu Calaça Menezes de Moraes sobre o conjunto público [Medical Cost Personal Datasets](https://www.kaggle.com/datasets/mirichoi0218/insurance). Os dados têm 1.338 linhas na origem e 1.337 após remover uma duplicata exata, conforme o tratamento da EDA.

## Aplicação publicada

O endereço público do app será registrado aqui depois da publicação e da conferência em janela anônima.

## Os dois painéis

| Painel | Conteúdo | Interação |
| --- | --- | --- |
| 1. Laboratório de distribuição e correlação | Mapa de calor Pearson/Spearman e um histograma para cada variável quantitativa selecionada | Seletor de variáveis, intervalo de custo, região, tabagismo e método de correlação |
| 2. Indicadores da carteira | Quatro KPIs; boxplot de custo por tabagismo; parcela de custos altos por faixa etária; mapa de calor da mediana por faixa de IMC e tabagismo | Os filtros de custo, região e tabagismo atualizam métricas e gráficos |

O público do segundo painel é um **analista de custos de uma carteira de seguros**. Os indicadores permitem localizar concentrações e diferenças para investigação. Não há inferência causal, diagnóstico, previsão, precificação nem decisão individual.

## Executar localmente

Testado com Python 3.13 e as versões fixadas em `requirements.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

O app lê apenas `data/clean/dataset.csv` por um caminho relativo ao projeto. O CSV tratado já está versionado, então a execução e o deploy não dependem de Kaggle nem de segredos. Para reconstruí-lo a partir da fonte pública:

```bash
python -m src.prepare_data
```

O tratamento reproduz o notebook: renomear colunas para português, traduzir categorias e remover duplicatas exatas. Outliers plausíveis são mantidos. Para executar a EDA original, instale também `requirements-eda.txt`. O [notebook de preparação](notebooks/preparacao-dados.ipynb) documenta a exportação da base tratada.

## Organização

```text
app.py                         Dois painéis Streamlit
src/                           Leitura, preparação e cálculos
data/clean/dataset.csv         Base pública tratada usada no app
notebooks/                      EDA original e preparação reprodutível
entregas/                       Dois rascunhos e justificativa das métricas
prompts/                        Registro do uso de IA
.streamlit/config.toml          Identidade visual
```

Os [rascunhos e a justificativa](entregas/README.md) acompanham o código. A [declaração de uso de IA](prompts/declaracao-uso-ia.md) descreve a assistência recebida.

## Definições e limites

- **Custo alto:** custo faturado igual ou superior ao percentil 75 da **base tratada completa**. O limiar fica fixo ao filtrar, preservando a referência.
- **Concentração no topo 10%:** soma dos custos dos `ceil(10% × n)` registros de maior custo dividida pela soma de custos do recorte.
- **Amostras pequenas:** o app omite indicadores e visuais com menos de 10 registros; grupos de comparação do painel 2 com menos de 10 registros são omitidos.
- **Privacidade:** a base é pública, não contém nome, contato ou identificador pessoal, e os gráficos recebem apenas dados agregados do servidor. Nenhum arquivo de segredos é versionado.
- **Interpretação:** `charges` corresponde a custos individuais faturados na base. A fonte não especifica um período de referência; portanto, o painel não os chama de custos anuais.

Fonte de dados: [Kaggle — Medical Cost Personal Datasets](https://www.kaggle.com/datasets/mirichoi0218/insurance), que aponta para o [repositório de origem dos conjuntos Machine Learning with R](https://github.com/stedy/Machine-Learning-with-R-datasets). A ficha do Kaggle informa licença para base e conteúdo. Os gráficos e indicadores são descritivos e podem refletir composição de grupos ou fatores não observados.
