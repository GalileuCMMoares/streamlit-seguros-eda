# [IA] Codex – cenários de teste da aplicação e dos agregados usados nos gráficos.
"""Cenários de interação relevantes para a entrega."""

import unittest
from math import ceil
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.analytics import (
    HIGH_COST_LIMIT,
    SMOKING_LABELS,
    age_smoking_mean_summary,
    filter_data,
    histogram_summary,
    smoking_group_summary,
    smoking_histogram_summary,
)
from src.data_loader import load_data

APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


class DashboardTests(unittest.TestCase):
    def test_default_panels_and_widgets(self):
        app = AppTest.from_file(APP_PATH, default_timeout=30).run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(2, len(app.tabs))
        self.assertEqual(3, len(app.metric))
        self.assertEqual(8, len(app.get("vega_lite_chart")))
        self.assertEqual(2, len(app.multiselect))
        self.assertEqual(1, len(app.slider))
        self.assertEqual(1, len(app.selectbox))
        self.assertEqual(1, len(app.radio))

    def test_filters_and_variable_edge_cases(self):
        app = AppTest.from_file(APP_PATH, default_timeout=30).run()
        app.multiselect[0].set_value([]).run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(3, len(app.get("vega_lite_chart")))

        app.multiselect[0].set_value(["idade"]).run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(4, len(app.get("vega_lite_chart")))

        app.multiselect[0].set_value(["idade", "custo"]).run()
        app.radio[0].set_value("Pearson").run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(6, len(app.get("vega_lite_chart")))

        initial_high_cost_metric = app.metric[1].value
        app.slider[0].set_value((1100, 20000)).run()
        self.assertEqual([], list(app.exception))
        self.assertNotEqual(initial_high_cost_metric, app.metric[1].value)

        app.multiselect[1].set_value(["Northeast"]).run()
        app.selectbox[0].set_value("Sim").run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(2, len(app.tabs))

        app.multiselect[1].set_value([]).run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(0, len(app.metric))
        self.assertEqual(0, len(app.get("vega_lite_chart")))

    def test_group_metrics_and_deciles_are_calculated_separately(self):
        data = load_data()
        self.assertEqual(1337, len(data))
        regions = sorted(data["regiao"].unique().tolist())
        subset = filter_data(data, (1100, 20000), regions, "Todos")
        summary = smoking_group_summary(subset)
        self.assertEqual(set(SMOKING_LABELS), set(summary["fumante"]))
        self.assertEqual(len(subset), int(summary["n"].sum()))
        for row in summary.itertuples(index=False):
            group = subset.loc[subset["fumante"] == row.fumante, "custo"]
            self.assertEqual(len(group), row.n)
            self.assertAlmostEqual(
                float(group.ge(HIGH_COST_LIMIT).mean() * 100),
                row.custos_altos_pct,
            )
            top_count = max(1, ceil(len(group) * 0.10))
            expected = float(group.nlargest(top_count).sum() / group.sum() * 100)
            self.assertAlmostEqual(expected, row.concentracao_top10_pct)
            expected_bottom = float(group.nsmallest(top_count).sum() / group.sum() * 100)
            self.assertAlmostEqual(expected_bottom, row.concentracao_bottom10_pct)

    def test_charts_receive_aggregates(self):
        data = load_data()
        for variable in ["idade", "imc", "filhos", "custo"]:
            frequency = histogram_summary(data, variable)
            self.assertEqual(len(data), int(frequency["registros"].sum()))
            self.assertLess(len(frequency), len(data))
        histograms = smoking_histogram_summary(data)
        self.assertEqual({"Não", "Sim"}, set(histograms["fumante"]))
        self.assertEqual({15}, set(histograms.groupby("fumante").size()))
        self.assertTrue((histograms.groupby("fumante")["registros"].sum() >= 10).all())
        shared_bins = {
            group: list(zip(frame["inicio"], frame["fim"]))
            for group, frame in histograms.groupby("fumante")
        }
        self.assertEqual(shared_bins["Não"], shared_bins["Sim"])
        age_groups = age_smoking_mean_summary(data)
        self.assertTrue((age_groups["n"] >= 10).all())
        self.assertEqual({"Não", "Sim"}, set(age_groups["fumante"]))


if __name__ == "__main__":
    unittest.main()
