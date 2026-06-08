from datetime import date
from pathlib import Path

from fastapi import HTTPException, status

from src.application.repositories.read_repository import ReadRepository


class QueryService:
    def __init__(self, repository: ReadRepository):
        self.repository = repository

    def list_current_companies(self) -> list[dict]:
        return self.repository.list_current_companies()

    def get_company_latest(self, company_id: int) -> dict:
        row = self.repository.get_company_latest(company_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company {company_id} not found",
            )
        return row

    def get_company_versions(self, company_id: int) -> list[dict]:
        rows = self.repository.get_company_versions(company_id)
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company {company_id} not found",
            )
        return rows

    def get_company_history(self, company_id: int) -> list[dict]:
        rows = self.repository.get_company_history(company_id)
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No history found for company {company_id}",
            )
        return rows

    def compare_companies_as_of(self, company_ids: list[int], as_of_date: date) -> list[dict]:
        if not company_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="company_ids must contain at least one id",
            )
        return self.repository.compare_companies_as_of(company_ids, as_of_date)

    def list_snapshots(
        self,
        company_id: int | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        sector: str | None = None,
        country: str | None = None,
        currency: str | None = None,
    ) -> list[dict]:
        return self.repository.list_snapshots(
            company_id=company_id,
            from_date=from_date,
            to_date=to_date,
            sector=sector,
            country=country,
            currency=currency,
        )

    def get_snapshot(self, snapshot_id: int) -> dict:
        row = self.repository.get_snapshot(snapshot_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Snapshot {snapshot_id} not found",
            )
        return row

    def get_latest_snapshots(self) -> list[dict]:
        return self.repository.get_latest_snapshots()

    def list_uploads(self) -> list[dict]:
        return self.repository.list_uploads()

    def get_upload_details(self, upload_id: int) -> dict:
        upload = self.repository.get_upload(upload_id)
        if upload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Upload {upload_id} not found",
            )
        snapshots = self.repository.get_upload_snapshots(upload_id)
        return {"upload": upload, "snapshots": snapshots}

    def list_upload_stats(self) -> list[dict]:
        return self.repository.list_upload_stats()

    def get_upload_file_path(self, upload_id: int) -> Path:
        file_path = self.repository.get_upload_file_path(upload_id)
        if file_path is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Upload {upload_id} not found",
            )
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Upload file not found at path: {file_path}",
            )
        return file_path
