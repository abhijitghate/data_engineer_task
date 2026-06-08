from datetime import datetime

from fastapi.testclient import TestClient

from src.application.deps import get_query_service
from src.application.main import app


class StubPipelineQueryService:
    def list_pipeline_runs(self):
        return [
            {
                "run_id": 12,
                "discussion_version": "v2",
                "started_at": datetime(2024, 1, 1, 10, 0, 0),
                "finished_at": datetime(2024, 1, 1, 10, 2, 0),
                "status": "success",
                "files_total": 2,
                "files_processed": 2,
                "files_succeeded": 2,
                "files_failed": 0,
                "files_skipped": 0,
                "quality_completeness_avg": 0.95,
                "quality_validity_avg": 0.98,
                "quality_warning_count": 1,
                "extract_ms_total": 120,
                "validate_ms_total": 80,
                "transform_ms_total": 40,
                "load_ms_total": 110,
                "duration_ms": 350,
                "error_summary": None,
            }
        ]

    def get_pipeline_run(self, run_id: int):
        return self.list_pipeline_runs()[0] if run_id == 12 else None

    def get_pipeline_run_quality(self, run_id: int):
        run = self.get_pipeline_run(run_id)
        if run is None:
            return None
        return {
            "run": run,
            "files": [
                {
                    "processed_file_id": 101,
                    "run_id": 12,
                    "file_name": "corporates_A_1.xlsm",
                    "file_path": "data/corporates_A_1.xlsm",
                    "file_checksum": "abc",
                    "discussion_version": "v2",
                    "status": "success",
                    "upload_id": 1,
                    "company_id": 1,
                    "company_version_id": 2,
                    "snapshot_id": 9,
                    "quality_completeness_rate": 1.0,
                    "quality_validity_rate": 1.0,
                    "quality_warning_count": 0,
                    "quality_warnings": None,
                    "extract_ms": 50,
                    "validate_ms": 30,
                    "transform_ms": 20,
                    "load_ms": 40,
                    "total_ms": 140,
                    "error_message": None,
                    "processed_at": datetime(2024, 1, 1, 10, 1, 0),
                }
            ],
            "artifact": {"run_id": 12, "summary": {"files_total": 2}},
        }


def _override_service():
    return StubPipelineQueryService()


def test_list_pipeline_runs_endpoint():
    app.dependency_overrides[get_query_service] = _override_service
    client = TestClient(app)
    response = client.get("/pipeline/runs")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["run_id"] == 12


def test_get_pipeline_run_endpoint():
    app.dependency_overrides[get_query_service] = _override_service
    client = TestClient(app)
    response = client.get("/pipeline/runs/12")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_get_pipeline_run_quality_endpoint():
    app.dependency_overrides[get_query_service] = _override_service
    client = TestClient(app)
    response = client.get("/pipeline/runs/12/quality")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["run_id"] == 12
    assert payload["files"][0]["processed_file_id"] == 101
