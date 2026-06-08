from datetime import date, datetime

from fastapi.testclient import TestClient

from src.application.deps import get_query_service
from src.application.main import app


class StubQueryService:
    def list_current_companies(self):
        return [
            {
                "company_id": 1,
                "company_version_id": 10,
                "company_name": "Acme",
                "sector_name": "Industrials",
                "country_name": "Germany",
                "currency_code": "EUR",
                "accounting_principles": "IFRS",
                "end_of_business_month": "December",
                "company_valid_from": datetime(2024, 1, 1),
                "company_valid_to": datetime(9999, 1, 1),
                "is_current_company_version": True,
            }
        ]

    def compare_companies_as_of(self, company_ids: list[int], as_of_date: date):
        snapshots = [
            {
                "company_id": 1,
                "company_version_id": 10,
                "company_name": "Acme",
                "sector_name": "Industrials",
                "country_name": "Germany",
                "currency_code": "EUR",
                "as_of_snapshot_id": 100,
                "as_of_snapshot_ingested_at": datetime(2024, 1, 10),
                "discussion_version": "v1",
            },
            {
                "company_id": 1,
                "company_version_id": 10,
                "company_name": "Acme",
                "sector_name": "Industrials",
                "country_name": "Germany",
                "currency_code": "EUR",
                "as_of_snapshot_id": 101,
                "as_of_snapshot_ingested_at": datetime(2024, 2, 10),
                "discussion_version": "v2",
            },
        ]
        return [
            row
            for row in snapshots
            if row["company_id"] in company_ids
            and row["as_of_snapshot_ingested_at"].date() <= as_of_date
        ][:1]

    def get_latest_snapshots(self):
        return [
            {
                "snapshot_id": 200,
                "upload_id": 1,
                "file_name": "corporates_A_1.xlsm",
                "storage_path": "data/corporates_A_1.xlsm",
                "discussion_version": "v1",
                "uploaded_at": datetime(2024, 1, 1),
                "upload_status": "success",
                "company_id": 1,
                "company_version_id": 10,
                "company_name": "Acme",
                "sector_name": "Industrials",
                "country_name": "Germany",
                "currency_code": "EUR",
                "accounting_principles": "IFRS",
                "end_of_business_month": "December",
                "segmentation_criteria_name": "Segment A",
                "business_risk_profile": "bbb",
                "blended_industry_risk_profile": "bbb",
                "competitive_positioning": "bbb",
                "market_share": "bbb",
                "diversification": "bbb",
                "operating_profitability": "bbb",
                "sector_or_company_specific_factor_1": "bbb",
                "sector_or_company_specific_factor_2": "bbb",
                "financial_risk_profile": "bbb",
                "leverage": "bbb",
                "interest_cover": "bbb",
                "cash_flow_cover": "bbb",
                "liquidity_assessment": "bbb",
                "snapshot_ingested_at": datetime(2024, 1, 2),
                "snapshot_valid_from": datetime(2024, 1, 2),
                "snapshot_valid_to": datetime(9999, 1, 1),
                "snapshot_status": "success",
            }
        ]

    def list_upload_stats(self):
        return [
            {
                "upload_id": 1,
                "file_name": "corporates_A_1.xlsm",
                "storage_path": "data/corporates_A_1.xlsm",
                "discussion_version": "v1",
                "uploaded_at": datetime(2024, 1, 1),
                "upload_status": "success",
                "file_checksum": "abc",
                "snapshot_count": 1,
                "company_count": 1,
                "metric_row_count": 1,
                "first_snapshot_at": datetime(2024, 1, 1),
                "last_snapshot_at": datetime(2024, 1, 1),
            }
        ]


def _override_service():
    return StubQueryService()


def test_companies_compare_endpoint_point_in_time():
    app.dependency_overrides[get_query_service] = _override_service
    client = TestClient(app)
    response = client.get(
        "/companies/compare",
        params={"company_ids": [1], "as_of_date": "2024-01-15"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["as_of_snapshot_id"] == 100


def test_snapshots_latest_endpoint():
    app.dependency_overrides[get_query_service] = _override_service
    client = TestClient(app)
    response = client.get("/snapshots/latest")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["snapshot_id"] == 200


def test_upload_stats_endpoint():
    app.dependency_overrides[get_query_service] = _override_service
    client = TestClient(app)
    response = client.get("/uploads/stats")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["snapshot_count"] == 1
