from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PipelineRunResponse(BaseModel):
    run_id: int
    discussion_version: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    files_total: int
    files_processed: int
    files_succeeded: int
    files_failed: int
    files_skipped: int
    quality_completeness_avg: float | None
    quality_validity_avg: float | None
    quality_warning_count: int
    extract_ms_total: int
    validate_ms_total: int
    transform_ms_total: int
    load_ms_total: int
    duration_ms: int | None
    error_summary: str | None


class ProcessedFileResponse(BaseModel):
    processed_file_id: int
    run_id: int
    file_name: str
    file_path: str
    file_checksum: str
    discussion_version: str
    status: str
    upload_id: int | None
    company_id: int | None
    company_version_id: int | None
    snapshot_id: int | None
    quality_completeness_rate: float | None
    quality_validity_rate: float | None
    quality_warning_count: int | None
    quality_warnings: str | None
    extract_ms: int | None
    validate_ms: int | None
    transform_ms: int | None
    load_ms: int | None
    total_ms: int | None
    error_message: str | None
    processed_at: datetime


class PipelineRunQualityResponse(BaseModel):
    run: PipelineRunResponse
    files: list[ProcessedFileResponse]
    artifact: dict[str, Any] | None
