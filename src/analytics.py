# [IA] Codex – implementação e revisão dos cálculos agregados dos dashboards.
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
SMOKING_LABELS = ["Não", "Sim"]
HIGH_COST_LIMIT = 20_000
HISTOGRAM_BINS = 15
MIN_GROUP = 10


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
    return grouped


def histogram_summary(data: pd.DataFrame, variable: str) -> pd.DataFrame:
    """Agrega no servidor para não enviar as linhas individuais ao gráfico."""
    if variable == "filhos":
        counts = data[variable].value_counts().reindex(range(6), fill_value=0)
        return pd.DataFrame({"categoria": counts.index, "registros": counts.values})
    counts, edges = np.histogram(data[variable], bins=24)
    return pd.DataFrame(
        {"inicio": edges[:-1], "fim": edges[1:], "registros": counts}
    )


def smoking_group_summary(
    data: pd.DataFrame,
    high_cost_limit: float = HIGH_COST_LIMIT,
    min_group: int = MIN_GROUP,
) -> pd.DataFrame:
    """Resume indicadores por tabagismo; taxas só são publicadas para grupos maiores."""
    rows: list[dict[str, float | int | str]] = []
    for smoking, group in data.groupby("fumante", sort=False):
        n = len(group)
        costs = group["custo"]
        row: dict[str, float | int | str] = {
            "fumante": smoking,
            "n": n,
            "mediana": float(costs.median()),
            "custo_medio": float(costs.mean()),
            "custos_altos_pct": float(costs.ge(high_cost_limit).mean() * 100)
            if n >= min_group else np.nan,
            "concentracao_top10_pct": np.nan,
            "concentracao_bottom10_pct": np.nan,
        }
        if n >= min_group:
            decile_count = max(1, ceil(n * 0.10))
            total_cost = float(costs.sum())
            row["concentracao_top10_pct"] = (
                float(costs.nlargest(decile_count).sum() / total_cost * 100)
                if total_cost else np.nan
            )
            row["concentracao_bottom10_pct"] = (
                float(costs.nsmallest(decile_count).sum() / total_cost * 100)
                if total_cost else np.nan
            )
        rows.append(row)
    return pd.DataFrame(rows, columns=[
        "fumante", "n", "mediana", "custo_medio", "custos_altos_pct",
        "concentracao_top10_pct", "concentracao_bottom10_pct",
    ])


def smoking_histogram_summary(
    data: pd.DataFrame,
    bins: int = HISTOGRAM_BINS,
    min_group: int = MIN_GROUP,
) -> pd.DataFrame:
    """Gera histogramas por grupo usando os mesmos 15 limites de custo."""
    eligible = data.groupby("fumante")["custo"].size()
    eligible = eligible[eligible >= min_group].index.tolist()
    if not eligible:
        return pd.DataFrame(columns=["fumante", "inicio", "fim", "registros"])

    comparison = data.loc[data["fumante"].isin(eligible)]
    edges = np.histogram_bin_edges(comparison["custo"], bins=bins)
    rows: list[dict[str, float | int | str]] = []
    for smoking in SMOKING_LABELS:
        if smoking not in eligible:
            continue
        counts, _ = np.histogram(
            comparison.loc[comparison["fumante"] == smoking, "custo"], bins=edges
        )
        rows.extend(
            {"fumante": smoking, "inicio": float(edges[i]),
             "fim": float(edges[i + 1]), "registros": int(count)}
            for i, count in enumerate(counts)
        )
    return pd.DataFrame(rows)


def age_smoking_mean_summary(
    data: pd.DataFrame,
    min_group: int = MIN_GROUP,
) -> pd.DataFrame:
    """Calcula custo médio por faixa etária e tabagismo, omitindo células pequenas."""
    grouped = add_groups(data)
    result = (
        grouped.groupby(["faixa_etaria", "fumante"], observed=True)
        .agg(n=("custo", "size"), custo_medio=("custo", "mean"))
        .reset_index()
    )
    return result.loc[result["n"] >= min_group]
