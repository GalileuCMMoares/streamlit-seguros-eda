# Observatório de custos de seguro

Aplicação Streamlit construída a partir da [EDA original](notebooks/eda-original.ipynb) de Galileu Calaça Menezes de Moraes sobre o conjunto público [Medical Cost Personal Datasets](https://www.kaggle.com/datasets/mirichoi0218/insurance). Os dados têm 1.338 linhas na origem e 1.337 após remover uma duplicata exata, conforme o tratamento da EDA.

## Aplicação publicada

[Abrir o Observatório de custos no Streamlit Community Cloud](https://galileu-seguros-eda.streamlit.app/)

## Os dois painéis

| Painel | Conteúdo | Interação |
| --- | --- | --- |
| 1. Laboratório de distribuição e correlação | Mapa de calor Pearson/Spearman e um histograma para cada variável quantitativa selecionada | Seletor de variáveis, intervalo de custo, região, tabagismo e método de correlação |
| 2. Comparação por tabagismo | Três medidas comparadas entre não fumantes e fumantes; barras de custo mediano, histogramas de contagem e barras de custo médio por idade | Os filtros de custo, região e tabagismo atualizam medidas e gráficos |

O público do segundo painel são **pessoas fumantes**, com comparação explícita a pessoas não fumantes. O painel resume diferenças observadas na amostra; não afirma que o tabagismo causou essas diferenças. Não é um diagnóstico ou estimativa do custo de saúde de uma pessoa.

As três medidas são: percentual com custo faturado de pelo menos US$ 20.000; parcela do custo total representada pelos 10% de menores custos em cada grupo; e parcela representada pelos 10% de maiores custos. Os dois decís são calculados separadamente entre fumantes e não fumantes. Os gráficos mostram a mediana com os valores escritos, histogramas em contagem com 15 intervalos e limites comuns, e custo médio por faixa etária separado por tabagismo.

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

Os [rascunhos, a justificativa e a validação do app publicado](entregas/README.md) acompanham o código. A [declaração de uso de IA](prompts/declaracao-uso-ia.md) descreve a assistência recebida.

## Definições e limites

- **Custo alto:** custo faturado igual ou superior a **US$ 20.000**. O mesmo limite é aplicado a fumantes e não fumantes e permanece fixo ao filtrar.
- **Custos nos 10% mais baixos:** calculados separadamente por tabagismo. Para cada grupo, divide-se a soma dos `ceil(10% × n)` menores custos pela soma dos custos de todo o grupo.
- **Concentração nos 10% mais altos:** calculada separadamente por tabagismo. Para cada grupo, divide-se a soma dos `ceil(10% × n)` maiores custos pela soma dos custos de todo o grupo.
- **Histograma do painel 2:** 15 intervalos definidos com limites comuns entre os grupos e contagem no eixo vertical.
- **Amostras pequenas:** taxas e gráficos comparativos omitem grupos ou combinações com menos de 10 registros; a contagem da amostra filtrada permanece indicada acima dos painéis.
- **Privacidade:** a base é pública, não contém nome, contato ou identificador direto, e os gráficos recebem apenas dados agregados do servidor. Nenhum arquivo de segredos é versionado.
- **Interpretação:** `charges` corresponde a custos individuais faturados na base. A fonte não especifica um período de referência; portanto, o painel não os chama de custos anuais.

Fonte de dados: [Kaggle — Medical Cost Personal Datasets](https://www.kaggle.com/datasets/mirichoi0218/insurance), que aponta para o [repositório de origem dos conjuntos Machine Learning with R](https://github.com/stedy/Machine-Learning-with-R-datasets). A ficha do Kaggle informa licença para base e conteúdo. Os gráficos e indicadores são descritivos e podem refletir composição de grupos ou fatores não observados.
