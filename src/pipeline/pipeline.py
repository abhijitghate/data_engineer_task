import argparse
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from sqlalchemy.exc import SQLAlchemyError

from src.database import models
from src.database.database import SessionLocal
from src.pipeline.loader import load_db_ready_data
from src.pipeline.logging_utils import (
    clear_log_context,
    configure_logging,
    set_log_context,
)
from src.pipeline.parser import parse_excel_master
from src.pipeline.transformer import transform_to_db_ready
from src.pipeline.validator import DataQualityReport, validate_data

DEFAULT_INPUT_FILES = [
    "data/corporates_A_1.xlsm",
    "data/corporates_A_2.xlsm",
    "data/corporates_B_1.xlsm",
    "data/corporates_B_2.xlsm",
]

LOGGER = logging.getLogger(__name__)


class StageTimings(TypedDict):
    extract_ms: int
    validate_ms: int
    transform_ms: int
    load_ms: int
    total_ms: int


class IngestionExecutionResult(TypedDict):
    load_result: dict
    quality_report: DataQualityReport
    timings: StageTimings


def _compute_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _create_pipeline_run(files_total: int, discussion_version: str) -> int:
    db = SessionLocal()
    try:
        run = models.PipelineRun(
            discussion_version=discussion_version,
            files_total=files_total,
            status="running",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.run_id
    finally:
        db.close()


def _update_pipeline_run_progress(
    run_id: int,
    files_processed: int,
    files_succeeded: int,
    files_failed: int,
    files_skipped: int,
) -> None:
    db = SessionLocal()
    try:
        run = (
            db.query(models.PipelineRun)
            .filter(models.PipelineRun.run_id == run_id)
            .first()
        )
        if run is None:
            return
        run.files_processed = files_processed
        run.files_succeeded = files_succeeded
        run.files_failed = files_failed
        run.files_skipped = files_skipped
        db.commit()
    finally:
        db.close()


def _finalize_pipeline_run(
    run_id: int,
    status: str,
    error_summary: str | None,
    duration_ms: int,
    extract_ms_total: int,
    validate_ms_total: int,
    transform_ms_total: int,
    load_ms_total: int,
    quality_completeness_avg: float | None,
    quality_validity_avg: float | None,
    quality_warning_count: int,
) -> None:
    db = SessionLocal()
    try:
        run = (
            db.query(models.PipelineRun)
            .filter(models.PipelineRun.run_id == run_id)
            .first()
        )
        if run is None:
            return
        run.status = status
        run.finished_at = datetime.now(timezone.utc)
        run.error_summary = error_summary
        run.duration_ms = duration_ms
        run.extract_ms_total = extract_ms_total
        run.validate_ms_total = validate_ms_total
        run.transform_ms_total = transform_ms_total
        run.load_ms_total = load_ms_total
        run.quality_completeness_avg = quality_completeness_avg
        run.quality_validity_avg = quality_validity_avg
        run.quality_warning_count = quality_warning_count
        db.commit()
    finally:
        db.close()


def _find_already_processed_file(
    file_checksum: str, discussion_version: str
) -> models.ProcessedFile | None:
    db = SessionLocal()
    try:
        return (
            db.query(models.ProcessedFile)
            .filter(
                models.ProcessedFile.file_checksum == file_checksum,
                models.ProcessedFile.discussion_version == discussion_version,
                models.ProcessedFile.status.in_(["success", "skipped_idempotent"]),
            )
            .order_by(models.ProcessedFile.processed_file_id.desc())
            .first()
        )
    finally:
        db.close()


def _record_processed_file(
    run_id: int,
    file_path: str,
    file_checksum: str,
    discussion_version: str,
    status: str,
    quality_report: DataQualityReport | None = None,
    timings: StageTimings | None = None,
    upload_id: int | None = None,
    company_id: int | None = None,
    company_version_id: int | None = None,
    snapshot_id: int | None = None,
    error_message: str | None = None,
) -> None:
    db = SessionLocal()
    try:
        row = models.ProcessedFile(
            run_id=run_id,
            file_name=Path(file_path).name,
            file_path=file_path,
            file_checksum=file_checksum,
            discussion_version=discussion_version,
            status=status,
            upload_id=upload_id,
            company_id=company_id,
            company_version_id=company_version_id,
            snapshot_id=snapshot_id,
            quality_completeness_rate=(
                quality_report["completeness_rate"] if quality_report else None
            ),
            quality_validity_rate=quality_report["validity_rate"] if quality_report else None,
            quality_warning_count=quality_report["warning_count"] if quality_report else None,
            quality_warnings=(
                " | ".join(quality_report["warnings"])[:1900] if quality_report else None
            ),
            extract_ms=timings["extract_ms"] if timings else None,
            validate_ms=timings["validate_ms"] if timings else None,
            transform_ms=timings["transform_ms"] if timings else None,
            load_ms=timings["load_ms"] if timings else None,
            total_ms=timings["total_ms"] if timings else None,
            error_message=error_message,
        )
        db.add(row)
        db.commit()
    finally:
        db.close()


def run_ingestion_pipeline(file_path: str, version: str) -> IngestionExecutionResult:
    db = SessionLocal()
    start = time.perf_counter()
    timings: StageTimings = {
        "extract_ms": 0,
        "validate_ms": 0,
        "transform_ms": 0,
        "load_ms": 0,
        "total_ms": 0,
    }
    try:
        step_start = time.perf_counter()
        parsed_data = parse_excel_master(file_path)
        timings["extract_ms"] = int((time.perf_counter() - step_start) * 1000)

        step_start = time.perf_counter()
        validated_data, quality_report = validate_data(parsed_data, version, file_path)
        timings["validate_ms"] = int((time.perf_counter() - step_start) * 1000)

        step_start = time.perf_counter()
        db_ready_data = transform_to_db_ready(validated_data)
        timings["transform_ms"] = int((time.perf_counter() - step_start) * 1000)

        step_start = time.perf_counter()
        load_result = load_db_ready_data(db, db_ready_data)
        timings["load_ms"] = int((time.perf_counter() - step_start) * 1000)
        timings["total_ms"] = int((time.perf_counter() - start) * 1000)
        return {
            "load_result": load_result,
            "quality_report": quality_report,
            "timings": timings,
        }
    finally:
        db.close()


def _is_retryable_exception(error: Exception) -> bool:
    if isinstance(error, (FileNotFoundError, ValueError)):
        return False
    if isinstance(error, (SQLAlchemyError, ConnectionError, TimeoutError)):
        return True
    if isinstance(error, OSError):
        return True
    return False


def _run_ingestion_with_retry(
    file_path: str,
    version: str,
    max_retries: int,
    base_backoff_seconds: float,
) -> IngestionExecutionResult:
    attempt = 0
    while True:
        try:
            return run_ingestion_pipeline(file_path=file_path, version=version)
        except Exception as error:
            attempt += 1
            should_retry = _is_retryable_exception(error) and attempt <= max_retries
            if not should_retry:
                raise
            sleep_seconds = base_backoff_seconds * (2 ** (attempt - 1))
            LOGGER.warning(
                "retrying_ingestion",
                extra={
                    "event": "retrying_ingestion",
                    "attempt": attempt,
                    "max_retries": max_retries,
                    "error": str(error),
                    "backoff_seconds": sleep_seconds,
                },
            )
            time.sleep(sleep_seconds)


def _write_quality_artifact(run_id: int, report: dict) -> Path:
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = reports_dir / f"quality_run_{run_id}.json"
    artifact_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return artifact_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run ingestion pipeline for one or more input files."
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="One or more input file paths, e.g. data/corporates_A_1.xlsm. If omitted, defaults are used.",
    )
    parser.add_argument(
        "--version",
        default="v1",
        help="Discussion version applied to all provided files (default: v1).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for transient errors (default: 3).",
    )
    parser.add_argument(
        "--backoff-seconds",
        type=float,
        default=1.0,
        help="Base exponential backoff delay in seconds (default: 1.0).",
    )
    return parser


if __name__ == "__main__":
    configure_logging()
    args = _build_parser().parse_args()
    files_to_load = args.files or DEFAULT_INPUT_FILES
    run_started = time.perf_counter()
    run_id = _create_pipeline_run(
        files_total=len(files_to_load), discussion_version=args.version
    )
    set_log_context(run_id=run_id)
    LOGGER.info(
        "pipeline_run_started",
        extra={
            "event": "pipeline_run_started",
            "discussion_version": args.version,
            "files_total": len(files_to_load),
            "max_retries": args.max_retries,
            "backoff_seconds": args.backoff_seconds,
        },
    )

    files_processed = 0
    files_succeeded = 0
    files_failed = 0
    files_skipped = 0
    failures: list[str] = []
    extract_ms_total = 0
    validate_ms_total = 0
    transform_ms_total = 0
    load_ms_total = 0
    quality_completeness_values: list[float] = []
    quality_validity_values: list[float] = []
    quality_warning_count = 0
    quality_file_reports: list[dict] = []

    for file_path in files_to_load:
        checksum = ""
        try:
            checksum = _compute_sha256(file_path)
            set_log_context(run_id=run_id, file_path=file_path, file_checksum=checksum)
            existing = _find_already_processed_file(
                file_checksum=checksum,
                discussion_version=args.version,
            )
            if existing is not None:
                files_processed += 1
                files_skipped += 1
                _record_processed_file(
                    run_id=run_id,
                    file_path=file_path,
                    file_checksum=checksum,
                    discussion_version=args.version,
                    status="skipped_incremental",
                    upload_id=existing.upload_id,
                    company_id=existing.company_id,
                    company_version_id=existing.company_version_id,
                    snapshot_id=existing.snapshot_id,
                    error_message=(
                        "Skipped because checksum + discussion_version already processed."
                    ),
                )
                LOGGER.info(
                    "file_skipped_incremental",
                    extra={"event": "file_skipped_incremental"},
                )
                quality_file_reports.append(
                    {
                        "file_path": file_path,
                        "status": "skipped_incremental",
                    }
                )
                continue

            execution = _run_ingestion_with_retry(
                file_path=file_path,
                version=args.version,
                max_retries=args.max_retries,
                base_backoff_seconds=args.backoff_seconds,
            )
            result = execution["load_result"]
            quality_report = execution["quality_report"]
            timings = execution["timings"]

            row_status = (
                "skipped_idempotent"
                if result.get("idempotency_skipped")
                else "success"
            )
            files_processed += 1
            if row_status == "success":
                files_succeeded += 1
            else:
                files_skipped += 1

            extract_ms_total += timings["extract_ms"]
            validate_ms_total += timings["validate_ms"]
            transform_ms_total += timings["transform_ms"]
            load_ms_total += timings["load_ms"]
            quality_completeness_values.append(quality_report["completeness_rate"])
            quality_validity_values.append(quality_report["validity_rate"])
            quality_warning_count += quality_report["warning_count"]

            _record_processed_file(
                run_id=run_id,
                file_path=file_path,
                file_checksum=checksum,
                discussion_version=args.version,
                status=row_status,
                quality_report=quality_report,
                timings=timings,
                upload_id=result.get("upload_id"),
                company_id=result.get("company_id"),
                company_version_id=result.get("company_version_id"),
                snapshot_id=result.get("snapshot_id"),
            )
            LOGGER.info(
                "file_processed",
                extra={
                    "event": "file_processed",
                    "status": row_status,
                    "upload_id": result.get("upload_id"),
                    "company_id": result.get("company_id"),
                    "company_version_id": result.get("company_version_id"),
                    "snapshot_id": result.get("snapshot_id"),
                    "quality_completeness_rate": quality_report["completeness_rate"],
                    "quality_validity_rate": quality_report["validity_rate"],
                    "quality_warning_count": quality_report["warning_count"],
                    "extract_ms": timings["extract_ms"],
                    "validate_ms": timings["validate_ms"],
                    "transform_ms": timings["transform_ms"],
                    "load_ms": timings["load_ms"],
                    "total_ms": timings["total_ms"],
                },
            )
            quality_file_reports.append(
                {
                    "file_path": file_path,
                    "status": row_status,
                    "quality_report": quality_report,
                    "timings": timings,
                }
            )
        except Exception as error:
            files_processed += 1
            files_failed += 1
            failure_message = f"{Path(file_path).name}: {error}"
            failures.append(failure_message)
            if not checksum:
                try:
                    checksum = _compute_sha256(file_path)
                except Exception:
                    checksum = "unavailable"
            _record_processed_file(
                run_id=run_id,
                file_path=file_path,
                file_checksum=checksum,
                discussion_version=args.version,
                status="failed",
                error_message=str(error)[:1900],
            )
            quality_file_reports.append(
                {
                    "file_path": file_path,
                    "status": "failed",
                    "error": str(error),
                }
            )
            LOGGER.exception(
                "file_failed",
                extra={"event": "file_failed", "error": str(error)},
            )
        finally:
            _update_pipeline_run_progress(
                run_id=run_id,
                files_processed=files_processed,
                files_succeeded=files_succeeded,
                files_failed=files_failed,
                files_skipped=files_skipped,
            )
            clear_log_context()

    quality_completeness_avg = (
        round(sum(quality_completeness_values) / len(quality_completeness_values), 4)
        if quality_completeness_values
        else None
    )
    quality_validity_avg = (
        round(sum(quality_validity_values) / len(quality_validity_values), 4)
        if quality_validity_values
        else None
    )
    run_duration_ms = int((time.perf_counter() - run_started) * 1000)

    _finalize_pipeline_run(
        run_id=run_id,
        status="success" if files_failed == 0 else "failed",
        error_summary=" | ".join(failures)[:1900] if failures else None,
        duration_ms=run_duration_ms,
        extract_ms_total=extract_ms_total,
        validate_ms_total=validate_ms_total,
        transform_ms_total=transform_ms_total,
        load_ms_total=load_ms_total,
        quality_completeness_avg=quality_completeness_avg,
        quality_validity_avg=quality_validity_avg,
        quality_warning_count=quality_warning_count,
    )

    quality_artifact = {
        "run_id": run_id,
        "discussion_version": args.version,
        "summary": {
            "files_total": len(files_to_load),
            "files_processed": files_processed,
            "files_succeeded": files_succeeded,
            "files_failed": files_failed,
            "files_skipped": files_skipped,
            "quality_completeness_avg": quality_completeness_avg,
            "quality_validity_avg": quality_validity_avg,
            "quality_warning_count": quality_warning_count,
            "duration_ms": run_duration_ms,
        },
        "files": quality_file_reports,
    }
    artifact_path = _write_quality_artifact(run_id=run_id, report=quality_artifact)
    set_log_context(run_id=run_id)
    LOGGER.info(
        "quality_artifact_written",
        extra={"event": "quality_artifact_written", "artifact_path": str(artifact_path)},
    )

    if files_failed == 0:
        LOGGER.info(
            "pipeline_run_finished",
            extra={
                "event": "pipeline_run_finished",
                "status": "success",
                "files_processed": files_processed,
                "files_succeeded": files_succeeded,
                "files_failed": files_failed,
                "files_skipped": files_skipped,
                "duration_ms": run_duration_ms,
                "extract_ms_total": extract_ms_total,
                "validate_ms_total": validate_ms_total,
                "transform_ms_total": transform_ms_total,
                "load_ms_total": load_ms_total,
                "quality_completeness_avg": quality_completeness_avg,
                "quality_validity_avg": quality_validity_avg,
                "quality_warning_count": quality_warning_count,
            },
        )
    else:
        LOGGER.error(
            "pipeline_run_finished",
            extra={
                "event": "pipeline_run_finished",
                "status": "failed",
                "files_processed": files_processed,
                "files_succeeded": files_succeeded,
                "files_failed": files_failed,
                "files_skipped": files_skipped,
                "duration_ms": run_duration_ms,
                "error_summary": " | ".join(failures)[:1900],
            },
        )
        raise SystemExit(1)
    clear_log_context()
