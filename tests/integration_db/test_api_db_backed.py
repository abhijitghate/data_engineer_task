from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import text

from src.application.main import app
from src.database import models
from src.database.database import SessionLocal


def _truncate_warehouse_tables() -> None:
    sql = """
    TRUNCATE TABLE
      warehouse.fact_scope_credit_metrics,
      warehouse.bridge_company_snapshot_industry_risks,
      warehouse.bridge_company_snapshot_research_methodology,
      warehouse.fact_company_snapshots,
      warehouse.dimension_companies,
      warehouse.dimension_industry_risk_types,
      warehouse.dimension_rating_methodologies_applied,
      warehouse.dimension_segmentation_criteria,
      warehouse.dimension_currencies,
      warehouse.dimension_countries,
      warehouse.dimension_sectors,
      warehouse.upload_logs,
      warehouse.processed_files,
      warehouse.pipeline_runs
    RESTART IDENTITY CASCADE;
    """
    db = SessionLocal()
    try:
        db.execute(text(sql))
        db.commit()
    finally:
        db.close()


def _seed_snapshot_data() -> None:
    db = SessionLocal()
    try:
        sector = models.Sector(sector_name="Industrials")
        country = models.Country(country_name="Germany")
        currency = models.Currency(currency_code="EUR")
        segmentation = models.SegmentationCriteria(segmentation_criteria_name="Segment A")
        db.add_all([sector, country, currency, segmentation])
        db.flush()

        company = models.Company(
            company_id=1,
            company_name="Acme Corp",
            sector_id=sector.sector_id,
            country_id=country.country_id,
            currency_id=currency.currency_id,
            accounting_principles="IFRS",
            end_of_business_month="December",
            is_current=True,
        )
        db.add(company)
        db.flush()

        upload_1 = models.UploadLog(
            file_name="corporates_A_1.xlsm",
            storage_path="data/corporates_A_1.xlsm",
            discussion_version="v1",
            upload_status="success",
            file_checksum="checksum-a1",
        )
        upload_2 = models.UploadLog(
            file_name="corporates_A_2.xlsm",
            storage_path="data/corporates_A_2.xlsm",
            discussion_version="v2",
            upload_status="success",
            file_checksum="checksum-a2",
        )
        db.add_all([upload_1, upload_2])
        db.flush()

        snapshot_1 = models.CompanySnapshot(
            upload_id=upload_1.upload_id,
            company_version_id=company.company_version_id,
            segmentation_criteria_id=segmentation.segmentation_criteria_id,
            business_risk_profile="bbb",
            blended_industry_risk_profile="bbb",
            competitive_positioning="bbb",
            market_share="bbb",
            diversification="bbb",
            operating_profitability="bbb",
            sector_or_company_specific_factor_1="bbb",
            sector_or_company_specific_factor_2="bbb",
            financial_risk_profile="bbb",
            leverage="bbb",
            interest_cover="bbb",
            cash_flow_cover="bbb",
            liquidity_assessment="bbb",
            ingested_at=datetime(2024, 1, 10, 8, 0, tzinfo=timezone.utc),
        )
        snapshot_2 = models.CompanySnapshot(
            upload_id=upload_2.upload_id,
            company_version_id=company.company_version_id,
            segmentation_criteria_id=segmentation.segmentation_criteria_id,
            business_risk_profile="bb+",
            blended_industry_risk_profile="bb+",
            competitive_positioning="bb+",
            market_share="bb+",
            diversification="bb+",
            operating_profitability="bb+",
            sector_or_company_specific_factor_1="bb+",
            sector_or_company_specific_factor_2="bb+",
            financial_risk_profile="bb+",
            leverage="bb+",
            interest_cover="bb+",
            cash_flow_cover="bb+",
            liquidity_assessment="bb+",
            ingested_at=datetime(2024, 2, 10, 8, 0, tzinfo=timezone.utc),
        )
        db.add_all([snapshot_1, snapshot_2])

        run = models.PipelineRun(
            discussion_version="v2",
            status="success",
            files_total=2,
            files_processed=2,
            files_succeeded=2,
            files_failed=0,
            files_skipped=0,
            quality_completeness_avg=0.95,
            quality_validity_avg=0.97,
            quality_warning_count=1,
            extract_ms_total=40,
            validate_ms_total=30,
            transform_ms_total=20,
            load_ms_total=10,
            duration_ms=100,
        )
        db.add(run)
        db.flush()

        processed = models.ProcessedFile(
            run_id=run.run_id,
            file_name="corporates_A_2.xlsm",
            file_path="data/corporates_A_2.xlsm",
            file_checksum="checksum-a2",
            discussion_version="v2",
            status="success",
            upload_id=upload_2.upload_id,
            company_id=1,
            company_version_id=company.company_version_id,
            snapshot_id=snapshot_2.snapshot_id,
            quality_completeness_rate=0.95,
            quality_validity_rate=0.97,
            quality_warning_count=1,
            quality_warnings="Industry weights sum warning",
            extract_ms=20,
            validate_ms=15,
            transform_ms=10,
            load_ms=8,
            total_ms=53,
        )
        db.add(processed)
        db.commit()
    finally:
        db.close()


def setup_function(_function):
    _truncate_warehouse_tables()
    _seed_snapshot_data()
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "quality_run_1.json").write_text(
        '{"run_id": 1, "summary": {"files_total": 2}}', encoding="utf-8"
    )


def teardown_function(_function):
    artifact = Path("reports/quality_run_1.json")
    if artifact.exists():
        artifact.unlink()


def test_companies_compare_uses_real_db():
    client = TestClient(app)
    response = client.get(
        "/companies/compare",
        params={"company_ids": [1], "as_of_date": "2024-01-15"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["as_of_snapshot_id"] == 1
    assert payload[0]["discussion_version"] == "v1"


def test_pipeline_quality_endpoint_reads_db_and_artifact():
    client = TestClient(app)
    response = client.get("/pipeline/runs/1/quality")
    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["run_id"] == 1
    assert payload["files"][0]["file_name"] == "corporates_A_2.xlsm"
    assert payload["artifact"]["run_id"] == 1
