"""Dois painéis descritivos a partir da EDA de custos de seguro médico."""

from __future__ import annotations

from math import ceil, floor

import altair as alt
import pandas as pd
import streamlit as st

from src.analytics import (
    AGE_LABELS,
    BMI_LABELS,
    NUMERIC_LABELS,
    age_summary,
    bmi_smoking_summary,
    filter_data,
    histogram_summary,
    kpis,
    smoking_box_summary,
)
from src.data_loader import load_data


st.set_page_config(page_title="Observatório de custos | EDA", page_icon="📊", layout="wide")

NAVY = "#17324A"
TEAL = "#087E77"
MIN_GROUP = 10


def usd(value: float) -> str:
    return f"US$ {value:,.0f}".replace(",", ".")


def pct(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


@st.cache_data(show_spinner=False)
def data() -> pd.DataFrame:
    return load_data()


all_data = data()
base_high_cost = float(all_data["custo"].quantile(0.75))
region_options = sorted(all_data["regiao"].unique().tolist())
min_cost = floor(float(all_data["custo"].min()) / 100) * 100
max_cost = ceil(float(all_data["custo"].max()) / 100) * 100

st.title("Observatório de custos de seguro")
st.write(
    "Uma leitura exploratória da distribuição dos custos e dos grupos que merecem "
    "investigação por um **analista de custos de uma carteira de seguros**."
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
    st.header("Indicadores da carteira")
    st.write(
        "Visão para priorizar investigações sobre concentração de custos e diferenças "
        "entre grupos da amostra."
    )
    if len(filtered) < MIN_GROUP:
        st.warning("Os indicadores são exibidos apenas com 10 registros ou mais. Amplie os filtros.")
    else:
        metrics = kpis(filtered, base_high_cost)
        c1, c2 = st.columns(2)
        c1.metric("Registros avaliados", f"{metrics['n']:,}".replace(",", "."),
                  help="Tamanho da amostra após os filtros.")
        c2.metric("Custo mediano", usd(metrics["median_cost"]),
                  help="Valor central dos custos faturados na seleção.")
        c3, c4 = st.columns(2)
        c3.metric("Custos altos", pct(metrics["high_cost_pct"]),
                  help="Parcela com custo igual ou superior ao percentil 75 da base completa.")
        c4.metric("Concentração no topo 10%", pct(metrics["top_decile_share_pct"]),
                  help="Parcela da soma dos custos atribuída aos 10% de registros mais caros da seleção.")
        st.caption(
            f"Custo alto = valor ≥ {usd(base_high_cost)} (P75 da base tratada completa). "
            "Grupos com menos de 10 registros são omitidos dos gráficos."
        )

        left, right = st.columns(2)
        with left:
            st.subheader("Custos por tabagismo")
            by_smoker = smoking_box_summary(filtered)
            if by_smoker.empty:
                st.info("Nenhum grupo de tabagismo tem 10 registros nesta seleção.")
            else:
                base = alt.Chart(by_smoker).encode(
                    x=alt.X("fumante:N", sort=["Não", "Sim"], title="Fumante"),
                )
                whiskers = base.mark_rule(color=TEAL, strokeWidth=2).encode(
                    y=alt.Y("minimo:Q", title="Custo faturado (USD)"), y2="maximo:Q"
                )
                boxes = base.mark_bar(color=TEAL, size=64, opacity=0.7).encode(
                    y="q1:Q", y2="q3:Q",
                    tooltip=[
                        alt.Tooltip("fumante:N", title="Fumante"),
                        alt.Tooltip("n:Q", title="Registros"),
                        alt.Tooltip("q1:Q", title="Q1 (USD)", format=",.0f"),
                        alt.Tooltip("mediana:Q", title="Mediana (USD)", format=",.0f"),
                        alt.Tooltip("q3:Q", title="Q3 (USD)", format=",.0f"),
                    ],
                )
                medians = base.mark_tick(color=NAVY, thickness=3, size=70).encode(y="mediana:Q")
                chart = (whiskers + boxes + medians).properties(height=300)
                st.altair_chart(chart, width="stretch",
                                alt="Boxplot agregado do custo faturado por tabagismo.")
        with right:
            st.subheader("Custos altos por faixa etária")
            by_age = age_summary(filtered, base_high_cost)
            if by_age.empty:
                st.info("Nenhuma faixa etária tem 10 registros nesta seleção.")
            else:
                chart = (
                    alt.Chart(by_age)
                    .mark_bar(color=TEAL)
                    .encode(
                        x=alt.X("faixa_etaria:N", sort=AGE_LABELS, title="Idade (anos)"),
                        y=alt.Y("high_cost_pct:Q", title="Parcela de custos altos (%)",
                                scale=alt.Scale(domain=[0, 100])),
                        tooltip=[
                            alt.Tooltip("faixa_etaria:N", title="Faixa etária"),
                            alt.Tooltip("n:Q", title="Registros"),
                            alt.Tooltip("high_cost_pct:Q", title="Custos altos (%)", format=".1f"),
                        ],
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart, width="stretch",
                                alt="Gráfico de barras da participação de custos altos por faixa etária.")

        st.subheader("Custo mediano por faixa de IMC e tabagismo")
        by_bmi_smoking = bmi_smoking_summary(filtered)
        if by_bmi_smoking.empty:
            st.info("Nenhuma combinação de IMC e tabagismo tem 10 registros nesta seleção.")
        else:
            base = alt.Chart(by_bmi_smoking).encode(
                x=alt.X("faixa_imc:N", sort=BMI_LABELS, title="Faixa de IMC (kg/m²)"),
                y=alt.Y("fumante:N", sort=["Não", "Sim"], title="Fumante"),
            )
            cells = base.mark_rect().encode(
                color=alt.Color("median_cost:Q", title="Mediana (USD)",
                                scale=alt.Scale(range=["#E9F3F2", TEAL])),
                tooltip=[
                    alt.Tooltip("faixa_imc:N", title="Faixa de IMC"),
                    alt.Tooltip("fumante:N", title="Fumante"),
                    alt.Tooltip("n:Q", title="Registros"),
                    alt.Tooltip("median_cost:Q", title="Custo mediano (USD)", format=",.0f"),
                ],
            )
            labels = base.mark_text(fontSize=15).encode(
                text=alt.Text("median_cost:Q", format=",.0f"),
                color=alt.condition(
                    f"datum.median_cost > {float(by_bmi_smoking['median_cost'].median())}",
                    alt.value("white"), alt.value(NAVY),
                ),
            )
            st.altair_chart(
                (cells + labels).properties(height=220), width="stretch",
                alt="Mapa de calor do custo mediano por faixa de IMC e tabagismo, com números em USD.",
            )

st.divider()
st.caption(
    "Dados públicos e sem identificadores da fonte. Cada linha representa uma observação "
    "anônima. Os resultados são descritivos, não estimam efeito causal e não servem para "
    "precificar ou decidir sobre uma pessoa."
)
