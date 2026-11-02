"""Leitura local e validação do dado tratado."""

from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "clean" / "dataset.csv"
EXPECTED = {"idade", "sexo", "imc", "filhos", "fumante", "regiao", "custo"}


def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    if set(data.columns) != EXPECTED:
        raise ValueError("O CSV tratado não tem as colunas esperadas")
    return data
