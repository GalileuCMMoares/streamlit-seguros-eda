# [IA] Codex – implementação do esqueleto Streamlit, dos gráficos e da interação dos painéis.
"""Dois painéis descritivos a partir da EDA de custos de seguro médico."""

from __future__ import annotations

from math import ceil, floor

import altair as alt
import pandas as pd
import streamlit as st

from src.analytics import (
    AGE_LABELS,
    HIGH_COST_LIMIT,
    HISTOGRAM_BINS,
    MIN_GROUP,
    NUMERIC_LABELS,
    SMOKING_LABELS,
    age_smoking_mean_summary,
    filter_data,
    histogram_summary,
    smoking_group_summary,
    smoking_histogram_summary,
)
from src.data_loader import load_data


st.set_page_config(page_title="Observatório de custos | EDA", page_icon="📊", layout="wide")

NAVY = "#17324A"
TEAL = "#087E77"


def usd(value: float) -> str:
    return f"US$ {value:,.0f}".replace(",", ".")


def pct(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


@st.cache_data(show_spinner=False)
def data() -> pd.DataFrame:
    return load_data()


all_data = data()
region_options = sorted(all_data["regiao"].unique().tolist())
min_cost = floor(float(all_data["custo"].min()) / 100) * 100
max_cost = ceil(float(all_data["custo"].max()) / 100) * 100

st.title("Observatório de custos de seguro")
st.write(
    "Uma leitura exploratória da distribuição dos custos e uma comparação direta "
    "entre pessoas fumantes e não fumantes."
)

with st.sidebar:
    st.header("Filtros da análise")
    selected_variables = st.multiselect(
        "Variáveis quantitativas",
        options=list(NUMERIC_LABELS),
        default=list(NUMERIC_LABELS),
        format_func=lambda variable: NUMERIC_LABELS[variable],
        help="Controla o mapa de calor e quais histogramas aparecem no Laboratório.",
    )
    cost_range = st.slider(
        "Intervalo de custo faturado (USD)",
        min_value=min_cost,
        max_value=max_cost,
        value=(min_cost, max_cost),
        step=100,
        help="Exclui registros fora do intervalo em ambos os painéis; não altera o CSV original.",
    )
    selected_regions = st.multiselect(
        "Regiões",
        options=region_options,
        default=region_options,
        help="Filtra os dois painéis pelas regiões selecionadas.",
    )
    smoking_filter = st.selectbox(
        "Tabagismo", ["Todos", "Não", "Sim"],
        help="Filtra os dois painéis pela categoria de tabagismo.",
    )
    correlation_method = st.radio(
        "Método de correlação", ["Spearman", "Pearson"],
        horizontal=True,
        help="Spearman mede associação por postos; Pearson mede associação linear.",
    )
    st.caption("Fonte: Medical Cost Personal Datasets (Kaggle). Valores em USD.")

filtered = filter_data(all_data, cost_range, selected_regions, smoking_filter)
st.caption(f"**{len(filtered):,}** de **{len(all_data):,}** registros após os filtros.".replace(",", "."))

laboratory, portfolio = st.tabs(["1 · Laboratório de distribuição e correlação", "2 · Indicadores da carteira"])

with laboratory:
    st.header("Laboratório de distribuição e correlação")
    st.write("Selecione variáveis e ajuste o intervalo de custo para observar como os padrões mudam.")
    if len(filtered) < MIN_GROUP:
        st.warning("Os filtros retornaram menos de 10 registros. Amplie o intervalo ou selecione mais grupos.")
    else:
        st.subheader(f"Correlação de {correlation_method}")
        valid_variables = [v for v in selected_variables if filtered[v].nunique() > 1]
        if len(selected_variables) < 2:
            st.info("Selecione pelo menos duas variáveis quantitativas para o mapa de calor.")
        elif len(valid_variables) < 2:
            st.info("Pelo menos duas variáveis precisam variar na seleção atual para calcular a correlação.")
        else:
            if len(valid_variables) != len(selected_variables):
                st.info("Variáveis constantes nesta seleção foram omitidas apenas do mapa de calor.")
            corr = filtered[valid_variables].corr(method=correlation_method.lower())
            long_corr = (
                corr.rename_axis("variavel_y")
                .reset_index()
                .melt(id_vars="variavel_y", var_name="variavel_x", value_name="coeficiente")
            )
            label_order = valid_variables
            base = alt.Chart(long_corr).encode(
                x=alt.X("variavel_x:N", sort=label_order, title=None,
                        axis=alt.Axis(labelAngle=0, labelExpr="datum.label === 'imc' ? 'IMC' : datum.label === 'custo' ? 'Custo' : datum.label === 'idade' ? 'Idade' : 'Filhos'")),
                y=alt.Y("variavel_y:N", sort=label_order, title=None,
                        axis=alt.Axis(labelExpr="datum.label === 'imc' ? 'IMC' : datum.label === 'custo' ? 'Custo' : datum.label === 'idade' ? 'Idade' : 'Filhos'")),
            )
            heatmap = base.mark_rect().encode(
                color=alt.Color("coeficiente:Q", title="Coeficiente",
                                scale=alt.Scale(domain=[-1, 0, 1],
                                                range=["#C46C55", "#F4F7F6", TEAL])),
                tooltip=[
                    alt.Tooltip("variavel_x:N", title="Variável X"),
                    alt.Tooltip("variavel_y:N", title="Variável Y"),
                    alt.Tooltip("coeficiente:Q", title="Correlação", format=".2f"),
                ],
            )
            values = base.mark_text(fontSize=15).encode(
                text=alt.Text("coeficiente:Q", format=".2f"),
                color=alt.condition("abs(datum.coeficiente) > 0.55", alt.value("white"), alt.value(NAVY)),
            )
            st.altair_chart(
                (heatmap + values).properties(height=300), width="stretch",
                alt="Mapa de calor da correlação entre as variáveis quantitativas selecionadas.",
            )
        st.caption("A correlação descreve associação na amostra filtrada; não demonstra causalidade.")

        st.subheader("Distribuições")
        if not selected_variables:
            st.info("Selecione ao menos uma variável quantitativa para ver o histograma.")
        else:
            for start in range(0, len(selected_variables), 2):
                columns = st.columns(2)
                for column, variable in zip(columns, selected_variables[start : start + 2]):
                    frequency = histogram_summary(filtered, variable)
                    if variable == "filhos":
                        histogram = alt.Chart(frequency).mark_bar(color=TEAL).encode(
                            x=alt.X("categoria:O", title=NUMERIC_LABELS[variable]),
                            y=alt.Y("registros:Q", title="Registros"),
                            tooltip=["categoria:O", alt.Tooltip("registros:Q", title="Registros")],
                        )
                    else:
                        histogram = alt.Chart(frequency).mark_bar(color=TEAL).encode(
                            x=alt.X("inicio:Q", title=NUMERIC_LABELS[variable]),
                            x2="fim:Q",
                            y=alt.Y("registros:Q", title="Registros"),
                            tooltip=[
                                alt.Tooltip("inicio:Q", title="De", format=",.1f"),
                                alt.Tooltip("fim:Q", title="Até", format=",.1f"),
                                alt.Tooltip("registros:Q", title="Registros"),
                            ],
                        )
                    histogram = histogram.properties(height=220)
                    with column:
                        st.altair_chart(
                            histogram, width="stretch",
                            alt=f"Histograma de {NUMERIC_LABELS[variable].lower()} na seleção filtrada.",
                        )

with portfolio:
    st.header("Custos observados: fumantes e não fumantes")
    st.write(
        "Compare os custos médicos faturados que aparecem nesta base. As diferenças "
        "são descritivas e, por si só, não mostram que o tabagismo causou a diferença."
    )
    if len(filtered) < MIN_GROUP:
        st.warning("Há menos de 10 registros após os filtros. Amplie a seleção para comparar os grupos.")
    else:
        by_smoking = smoking_group_summary(filtered)

        def metric_pair(key: str, formatter) -> str:
            values = []
            for label in SMOKING_LABELS:
                matches = by_smoking.loc[by_smoking["fumante"] == label, key]
                if matches.empty or pd.isna(matches.iloc[0]):
                    values.append("—")
                else:
                    values.append(formatter(matches.iloc[0]))
            return " / ".join(values)

        m1, m2, m3 = st.columns(3)
        m1.metric(
            "Custos nos 10% mais baixos · Não / Sim",
            metric_pair("concentracao_bottom10_pct", pct),
            help="Para cada grupo, soma dos custos de seus 10% de registros mais baratos dividida pela soma dos custos do próprio grupo.",
        )
        m2.metric(
            f"Custos ≥ {usd(HIGH_COST_LIMIT)} · Não / Sim",
            metric_pair("custos_altos_pct", pct),
            help="Percentual de registros de cada grupo com custo faturado de pelo menos US$ 20.000.",
        )
        m3.metric(
            "Custos nos 10% mais altos · Não / Sim",
            metric_pair("concentracao_top10_pct", pct),
            help="Para cada grupo, soma dos custos de seus 10% de registros mais caros dividida pela soma dos custos do próprio grupo.",
        )
        st.caption(
            "Ordem dos valores: não fumantes / fumantes. O corte de custo alto é US$ 20.000. "
            "Os 10% de menores e maiores custos são calculados separadamente dentro de cada grupo. "
            "Taxas e gráficos omitem grupos ou faixas com menos de 10 registros. "
            "Para comparar ambos, deixe Tabagismo como “Todos”."
        )

        st.subheader("Custo mediano por grupo")
        median_data = by_smoking.loc[by_smoking["n"] >= MIN_GROUP]
        if median_data.empty:
            st.info("Nenhum grupo de tabagismo tem 10 registros nesta seleção.")
        else:
            bars = alt.Chart(median_data).mark_bar(color=TEAL).encode(
                x=alt.X("fumante:N", sort=SMOKING_LABELS, title="Tabagismo"),
                y=alt.Y("mediana:Q", title="Custo mediano (USD)",
                        axis=alt.Axis(format="$,.0f"), scale=alt.Scale(zero=True)),
                tooltip=[
                    alt.Tooltip("fumante:N", title="Grupo"),
                    alt.Tooltip("n:Q", title="Registros"),
                    alt.Tooltip("mediana:Q", title="Custo mediano (USD)", format="$,.0f"),
                ],
            )
            labels = alt.Chart(median_data).mark_text(dy=-8, color=NAVY).encode(
                x=alt.X("fumante:N", sort=SMOKING_LABELS),
                y="mediana:Q",
                text=alt.Text("mediana:Q", format="$,.0f"),
            )
            st.altair_chart((bars + labels).properties(height=300), width="stretch",
                            alt="Barras comparando a mediana dos custos faturados entre não fumantes e fumantes, com valores escritos.")

        st.subheader(f"Distribuição dos custos · {HISTOGRAM_BINS} intervalos, contagem de registros")
        hist_data = smoking_histogram_summary(filtered)
        if hist_data.empty:
            st.info("Não há grupos com pelo menos 10 registros para mostrar o histograma.")
        else:
            hist = alt.Chart(hist_data).mark_bar(color=TEAL, opacity=0.8).encode(
                x=alt.X("inicio:Q", title="Custo faturado (USD)",
                        axis=alt.Axis(format="$,.0f")),
                x2="fim:Q",
                y=alt.Y("registros:Q", title="Registros", scale=alt.Scale(zero=True)),
                tooltip=[
                    alt.Tooltip("fumante:N", title="Grupo"),
                    alt.Tooltip("inicio:Q", title="De (USD)", format="$,.0f"),
                    alt.Tooltip("fim:Q", title="Até (USD)", format="$,.0f"),
                    alt.Tooltip("registros:Q", title="Registros"),
                ],
            )
            chart = hist.facet(
                column=alt.Column("fumante:N", sort=SMOKING_LABELS, title="Tabagismo"),
                columns=2,
            ).resolve_scale(x="shared", y="shared").properties(spacing=24)
            st.altair_chart(
                chart, width="stretch",
                alt="Histogramas de contagem dos custos faturados por tabagismo, com 15 intervalos e escalas iguais.",
            )
            st.caption("Os dois grupos usam os mesmos 15 limites de custo e a mesma escala de contagem.")

        st.subheader("Custo médico médio por faixa etária")
        age_data = age_smoking_mean_summary(filtered)
        if age_data.empty:
            st.info("Nenhuma combinação de faixa etária e tabagismo tem 10 registros nesta seleção.")
        else:
            age_chart = alt.Chart(age_data).mark_bar().encode(
                x=alt.X("faixa_etaria:N", sort=AGE_LABELS, title="Faixa etária (anos)"),
                xOffset=alt.XOffset("fumante:N", sort=SMOKING_LABELS),
                y=alt.Y("custo_medio:Q", title="Custo médio faturado (USD)",
                        axis=alt.Axis(format="$,.0f"), scale=alt.Scale(zero=True)),
                color=alt.Color("fumante:N", sort=SMOKING_LABELS, title="Tabagismo",
                                scale=alt.Scale(domain=SMOKING_LABELS, range=[NAVY, TEAL])),
                tooltip=[
                    alt.Tooltip("faixa_etaria:N", title="Faixa etária"),
                    alt.Tooltip("fumante:N", title="Grupo"),
                    alt.Tooltip("n:Q", title="Registros"),
                    alt.Tooltip("custo_medio:Q", title="Custo médio (USD)", format="$,.0f"),
                ],
            ).properties(height=320)
            st.altair_chart(age_chart, width="stretch",
                            alt="Barras agrupadas do custo médico médio por faixa etária, comparando fumantes e não fumantes.")

st.divider()
st.caption(
    "Dados públicos da fonte, sem identificadores diretos. Os gráficos recebem "
    "resumos agregados. Os resultados são descritivos, não estimam efeito causal e não servem para "
    "precificar ou decidir sobre uma pessoa."
)
