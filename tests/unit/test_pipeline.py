from sqlalchemy.exc import SQLAlchemyError

from src.pipeline import pipeline


def test_run_ingestion_with_retry_retries_transient_errors(monkeypatch):
    calls = {"count": 0}

    def fake_run_ingestion_pipeline(file_path: str, version: str):
        calls["count"] += 1
        if calls["count"] < 3:
            raise SQLAlchemyError("transient db issue")
        return {
            "load_result": {"upload_id": 1},
            "quality_report": {
                "completeness_rate": 1.0,
                "validity_rate": 1.0,
                "warning_count": 0,
                "missing_required_fields": [],
                "invalid_metric_values": 0,
                "total_metric_values": 0,
                "warnings": [],
            },
            "timings": {
                "extract_ms": 1,
                "validate_ms": 1,
                "transform_ms": 1,
                "load_ms": 1,
                "total_ms": 4,
            },
        }

    monkeypatch.setattr(
        "src.pipeline.pipeline.run_ingestion_pipeline", fake_run_ingestion_pipeline
    )
    monkeypatch.setattr("src.pipeline.pipeline.time.sleep", lambda *_args, **_kwargs: None)

    result = pipeline._run_ingestion_with_retry(
        file_path="data/file.xlsm",
        version="v1",
        max_retries=3,
        base_backoff_seconds=0.01,
    )

    assert calls["count"] == 3
    assert result["load_result"]["upload_id"] == 1
