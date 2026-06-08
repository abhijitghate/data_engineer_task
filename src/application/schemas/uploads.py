from datetime import datetime

from pydantic import BaseModel

from src.application.schemas.snapshots import SnapshotResponse


class UploadResponse(BaseModel):
    upload_id: int
    file_name: str
    storage_path: str
    discussion_version: str
    uploaded_at: datetime
    upload_status: str
    file_checksum: str


class UploadStatsResponse(BaseModel):
    upload_id: int
    file_name: str
    storage_path: str
    discussion_version: str
    uploaded_at: datetime
    upload_status: str
    file_checksum: str
    snapshot_count: int
    company_count: int
    metric_row_count: int
    first_snapshot_at: datetime | None
    last_snapshot_at: datetime | None


class UploadDetailsResponse(BaseModel):
    upload: UploadResponse
    snapshots: list[SnapshotResponse]
