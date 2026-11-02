"""Cálculos usados pelos dois painéis."""

from __future__ import annotations

from math import ceil

import numpy as np
import pandas as pd


NUMERIC_LABELS = {
    "idade": "Idade (anos)",
    "imc": "IMC (kg/m²)",
    "filhos": "Filhos cobertos",
    "custo": "Custo faturado (USD)",
}
AGE_LABELS = ["18–25", "26–40", "41–55", "56+"]
BMI_LABELS = ["< 25", "25 a < 30", "≥ 30"]


def filter_data(
    data: pd.DataFrame,
    cost_range: tuple[int, int],
    regions: list[str],
    smoking: str,
) -> pd.DataFrame:
    selected = data.loc[
        data["custo"].between(*cost_range) & data["regiao"].isin(regions)
    ]
    if smoking != "Todos":
        selected = selected.loc[selected["fumante"] == smoking]
    return selected.copy()


def add_groups(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.copy()
    grouped["faixa_etaria"] = pd.cut(
        grouped["idade"], bins=[0, 25, 40, 55, float("inf")], labels=AGE_LABELS
    )
    grouped["faixa_imc"] = pd.cut(
        grouped["imc"], bins=[0, 25, 30, float("inf")], labels=BMI_LABELS,
        right=False,
    )
    return grouped


def kpis(data: pd.DataFrame, high_cost_limit: float) -> dict[str, float | int]:
    if data.empty:
        raise ValueError("Não há registros para calcular os indicadores")
    top_count = max(1, ceil(len(data) * 0.10))
    return {
        "n": len(data),
        "median_cost": float(data["custo"].median()),
        "high_cost_pct": float(data["custo"].ge(high_cost_limit).mean() * 100),
        "top_decile_share_pct": float(
            data["custo"].nlargest(top_count).sum() / data["custo"].sum() * 100
        ),
    }


def age_summary(data: pd.DataFrame, high_cost_limit: float) -> pd.DataFrame:
    grouped = add_groups(data)
    result = (
        grouped.groupby("faixa_etaria", observed=True)
        .agg(n=("custo", "size"), high_cost_count=("custo", lambda s: s.ge(high_cost_limit).sum()))
        .reset_index()
    )
    result["high_cost_pct"] = result["high_cost_count"] / result["n"] * 100
    return result.loc[result["n"] >= 10]


def bmi_smoking_summary(data: pd.DataFrame) -> pd.DataFrame:
    grouped = add_groups(data)
    result = (
        grouped.groupby(["faixa_imc", "fumante"], observed=True)
        .agg(n=("custo", "size"), median_cost=("custo", "median"))
        .reset_index()
    )
    return result.loc[result["n"] >= 10]


def histogram_summary(data: pd.DataFrame, variable: str) -> pd.DataFrame:
    """Agrega no servidor para não enviar as linhas individuais ao gráfico."""
    if variable == "filhos":
        counts = data[variable].value_counts().reindex(range(6), fill_value=0)
        return pd.DataFrame({"categoria": counts.index, "registros": counts.values})
    counts, edges = np.histogram(data[variable], bins=24)
    return pd.DataFrame(
        {"inicio": edges[:-1], "fim": edges[1:], "registros": counts}
    )


def smoking_box_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Cinco números do boxplot por grupo, omitindo grupos pequenos."""
    result = (
        data.groupby("fumante")
        .agg(
            n=("custo", "size"),
            minimo=("custo", "min"),
            q1=("custo", lambda s: s.quantile(0.25)),
            mediana=("custo", "median"),
            q3=("custo", lambda s: s.quantile(0.75)),
            maximo=("custo", "max"),
        )
        .reset_index()
    )
    return result.loc[result["n"] >= 10]
