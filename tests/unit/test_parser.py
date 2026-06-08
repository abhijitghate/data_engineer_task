import pandas as pd

from src.pipeline.parser import parse_excel_master


def test_parse_excel_master_extracts_company_name(monkeypatch):
    df = pd.DataFrame(
        [
            ["Rated entity", "Acme Corp"],
            ["CorporateSector", "Industrials"],
        ]
    )

    monkeypatch.setattr("src.pipeline.parser.pd.read_excel", lambda *args, **kwargs: df)

    result = parse_excel_master("data/mock.xlsm")

    assert result["company_name"] == "Acme Corp"
    assert result["corporate_sector"] == "Industrials"
