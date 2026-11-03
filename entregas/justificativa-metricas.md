# Rascunho para justificar as métricas

Este arquivo organiza as definições técnicas do Dashboard 2.

## Público e medidas confirmadas no diálogo

- Público: pessoas fumantes, com comparação explícita a pessoas não fumantes.
- Medidas escolhidas para o painel: proporção de custos faturados de pelo menos US$ 20.000; participação da soma dos custos dos 10% menores e dos 10% maiores valores **dentro de cada grupo**.
- Gráficos escolhidos: comparação das medianas; histogramas de contagem com 15 intervalos comuns; custo médico médio por faixa etária, separado por tabagismo.

## Definições usadas pelo app

| Medida | Definição operacional | Minha justificativa e o que quero comunicar (preencher com minhas palavras) |
| --- | --- | --- |
| Custos nos 10% mais baixos | Dentro de cada grupo, ordenam-se os custos; somam-se os `ceil(0,10 × n)` menores; divide-se essa soma pela soma de todos os custos do mesmo grupo. | _Explique por que escolheu essa medida e o que a comparação deve comunicar._ |
| Custos altos | Percentual de registros do grupo com custo faturado ≥ US$ 20.000. O mesmo limite vale para os dois grupos. | _Explique por que escolheu esse limite e o que deseja que o público entenda._ |
| Concentração nos 10% mais altos | Dentro de cada grupo, ordenam-se os custos; somam-se os `ceil(0,10 × n)` maiores; divide-se essa soma pela soma de todos os custos do mesmo grupo. | _Explique por que escolheu essa medida e o que a comparação deve mostrar._ |

O app compara custos faturados observados. A fonte não especifica um período, e a comparação descritiva não prova que fumar causou uma diferença.
