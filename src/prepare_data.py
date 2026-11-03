# [IA] Codex – implementação do script reprodutível de preparação da base.
"""Reproduz o tratamento mínimo usado na EDA original.

Uso: python -m src.prepare_data
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd


SOURCE_URL = "https://www.kaggle.com/api/v1/datasets/download/mirichoi0218/insurance"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "clean" / "dataset.csv"
EXPECTED_COLUMNS = ["age", "sex", "bmi", "children", "smoker", "region", "charges"]


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    if list(raw.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Colunas inesperadas: {list(raw.columns)}")

    data = raw.rename(
        columns={
            "age": "idade",
            "sex": "sexo",
            "bmi": "imc",
            "children": "filhos",
            "smoker": "fumante",
            "region": "regiao",
            "charges": "custo",
        }
    ).copy()
    data["sexo"] = data["sexo"].map({"female": "Feminino", "male": "Masculino"})
    data["fumante"] = data["fumante"].map({"yes": "Sim", "no": "Não"})
    data["regiao"] = data["regiao"].str.title()
    if data.isna().any().any():
        raise ValueError("A base contém valores ausentes ou categorias não reconhecidas")
    if (data[["idade", "imc", "custo"]] <= 0).any().any():
        raise ValueError("A base contém idade, IMC ou custo não positivo")
    return data.drop_duplicates().reset_index(drop=True)


def main() -> None:
    with urlopen(SOURCE_URL, timeout=30) as response:
        payload = response.read()
    with ZipFile(BytesIO(payload)) as archive:
        raw = pd.read_csv(archive.open("insurance.csv"))
    data = prepare(raw)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT, index=False)
    print(f"{len(raw)} registros de origem; {len(data)} após remover duplicatas; salvo em {OUTPUT}")


if __name__ == "__main__":
    main()
