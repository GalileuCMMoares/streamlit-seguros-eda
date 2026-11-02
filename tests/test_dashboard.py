"""Cenários de interação relevantes para a entrega."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.analytics import filter_data, histogram_summary, kpis, smoking_box_summary
from src.data_loader import load_data

APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


class DashboardTests(unittest.TestCase):
    def test_default_panels_and_widgets(self):
        app = AppTest.from_file(APP_PATH, default_timeout=30).run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(2, len(app.tabs))
        self.assertEqual(4, len(app.metric))
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

        app.slider[0].set_value((1100, 20000)).run()
        self.assertEqual([], list(app.exception))
        self.assertLess(int(app.metric[0].value.replace(".", "")), 1337)

        app.multiselect[1].set_value(["Northeast"]).run()
        app.selectbox[0].set_value("Sim").run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(2, len(app.tabs))

        app.multiselect[1].set_value([]).run()
        self.assertEqual([], list(app.exception))
        self.assertEqual(0, len(app.metric))
        self.assertEqual(0, len(app.get("vega_lite_chart")))

    def test_metrics_follow_filtered_data(self):
        data = load_data()
        self.assertEqual(1337, len(data))
        regions = sorted(data["regiao"].unique().tolist())
        subset = filter_data(data, (1100, 20000), regions, "Todos")
        baseline = float(data["custo"].quantile(0.75))
        summary = kpis(subset, baseline)
        self.assertLess(summary["n"], len(data))
        self.assertLess(summary["high_cost_pct"], 25.1)
        self.assertGreater(summary["top_decile_share_pct"], 0)

    def test_charts_receive_aggregates(self):
        data = load_data()
        for variable in ["idade", "imc", "filhos", "custo"]:
            frequency = histogram_summary(data, variable)
            self.assertEqual(len(data), int(frequency["registros"].sum()))
            self.assertLess(len(frequency), len(data))
        boxes = smoking_box_summary(data)
        self.assertEqual({"Não", "Sim"}, set(boxes["fumante"]))
        self.assertTrue((boxes["q1"] <= boxes["mediana"]).all())
        self.assertTrue((boxes["mediana"] <= boxes["q3"]).all())


if __name__ == "__main__":
    unittest.main()
