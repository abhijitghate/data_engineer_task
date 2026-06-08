from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.pipeline import loader


def test_invalidate_latest_snapshot_sets_valid_to():
    db = MagicMock()
    snapshot = SimpleNamespace(snapshot_id=42, valid_to=None)
    chain = db.query.return_value.join.return_value.filter.return_value.order_by.return_value
    chain.first.return_value = snapshot
    closed_at = datetime.now(timezone.utc)

    loader._invalidate_latest_snapshot_for_company(db, company_id=1, closed_at=closed_at)

    assert snapshot.valid_to == closed_at


def test_load_db_ready_data_short_circuits_for_existing_checksum(monkeypatch):
    db = MagicMock()
    db.begin.return_value.__enter__.return_value = None
    db.begin.return_value.__exit__.return_value = None

    monkeypatch.setattr(
        "src.pipeline.loader._get_upload_by_checksum",
        lambda *args, **kwargs: SimpleNamespace(upload_id=5),
    )
    monkeypatch.setattr(
        "src.pipeline.loader._get_latest_snapshot_for_upload",
        lambda *args, **kwargs: SimpleNamespace(snapshot_id=7, company_version_id=11),
    )

    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
        company_id=3
    )

    result = loader.load_db_ready_data(
        db,
        {
            "upload_log": {"file_checksum": "abc"},
            "company": {"company_name": "Acme"},
            "dimensions": {
                "sector_name": "x",
                "country_name": "x",
                "currency_code": "x",
                "segmentation_criteria_name": "x",
                "rating_methodology_applied_names": [],
                "industry_risk_type_names": [],
            },
        },
    )

    assert result["idempotency_skipped"] is True
    assert result["upload_id"] == 5
    assert result["company_version_id"] == 11
    assert result["snapshot_id"] == 7
