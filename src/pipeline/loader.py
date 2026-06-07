from datetime import datetime, timezone
from typing import Type

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import models
from src.pipeline.transformer import (
    DBReadyData,
    ResolvedReferences,
    build_insert_ready_data,
)


def _get_or_create_dimension(
    db: Session,
    model: Type,
    name_field: str,
    id_field: str,
    value: str,
) -> int:
    record = db.query(model).filter(getattr(model, name_field) == value).first()
    if record:
        return getattr(record, id_field)

    record = model(**{name_field: value})
    db.add(record)
    db.flush()
    return getattr(record, id_field)


def _resolve_map_ids(
    db: Session,
    model: Type,
    name_field: str,
    id_field: str,
    values: list[str],
) -> dict[str, int]:
    ids: dict[str, int] = {}
    for value in values:
        ids[value] = _get_or_create_dimension(db, model, name_field, id_field, value)
    return ids


def _find_or_create_upload(db: Session, upload_log: dict) -> int:
    record = (
        db.query(models.UploadLog)
        .filter(models.UploadLog.file_checksum == upload_log["file_checksum"])
        .first()
    )
    if record:
        return record.upload_id

    record = models.UploadLog(**upload_log)
    db.add(record)
    db.flush()
    return record.upload_id


def _upsert_company_current(
    db: Session,
    company_payload: dict,
) -> int:
    company_id = company_payload["company_id"]
    current = (
        db.query(models.Company)
        .filter(models.Company.company_id == company_id, models.Company.is_current.is_(True))
        .first()
    )

    if current is None:
        current = models.Company(**company_payload)
        db.add(current)
        db.flush()
        return current.company_surrogate_key

    unchanged = (
        current.company_name == company_payload["company_name"]
        and current.sector_id == company_payload["sector_id"]
        and current.country_id == company_payload["country_id"]
        and current.currency_id == company_payload["currency_id"]
        and current.accounting_principles == company_payload["accounting_principles"]
        and current.end_of_business_month == company_payload["end_of_business_month"]
    )
    if unchanged:
        return current.company_surrogate_key

    now = datetime.now(timezone.utc)
    current.is_current = False
    current.valid_to = now

    new_company = models.Company(**company_payload)
    db.add(new_company)
    db.flush()
    return new_company.company_surrogate_key


def _insert_snapshot(db: Session, snapshot_payload: dict) -> int:
    snapshot = models.CompanySnapshot(**snapshot_payload)
    db.add(snapshot)
    db.flush()
    return snapshot.snapshot_id


def _resolve_or_allocate_company_id(db: Session, company_name: str) -> int:
    current_company = (
        db.query(models.Company)
        .filter(
            models.Company.company_name == company_name, models.Company.is_current.is_(True)
        )
        .first()
    )
    if current_company:
        return current_company.company_id

    historical_company = (
        db.query(models.Company)
        .filter(models.Company.company_name == company_name)
        .order_by(models.Company.company_surrogate_key.desc())
        .first()
    )
    if historical_company:
        return historical_company.company_id

    max_company_id = db.query(func.max(models.Company.company_id)).scalar() or 0
    return int(max_company_id) + 1


def load_db_ready_data(
    db: Session,
    db_ready_data: DBReadyData,
) -> dict:
    with db.begin():
        company_id = _resolve_or_allocate_company_id(
            db, db_ready_data["company"]["company_name"]
        )

        sector_id = _get_or_create_dimension(
            db,
            models.Sector,
            "sector_name",
            "sector_id",
            db_ready_data["dimensions"]["sector_name"],
        )
        country_id = _get_or_create_dimension(
            db,
            models.Country,
            "country_name",
            "country_id",
            db_ready_data["dimensions"]["country_name"],
        )
        currency_id = _get_or_create_dimension(
            db,
            models.Currency,
            "currency_code",
            "currency_id",
            db_ready_data["dimensions"]["currency_code"],
        )
        segmentation_criteria_id = _get_or_create_dimension(
            db,
            models.SegmentationCriteria,
            "segmentation_criteria_name",
            "segmentation_criteria_id",
            db_ready_data["dimensions"]["segmentation_criteria_name"],
        )

        rating_methodology_ids = _resolve_map_ids(
            db,
            models.RatingMethodologyApplied,
            "rating_methodology_applied_name",
            "rating_methodology_applied_id",
            db_ready_data["dimensions"]["rating_methodology_applied_names"],
        )
        industry_risk_type_ids = _resolve_map_ids(
            db,
            models.IndustryRiskType,
            "industry_risk_type_name",
            "industry_risk_type_id",
            db_ready_data["dimensions"]["industry_risk_type_names"],
        )

        upload_id = _find_or_create_upload(db, db_ready_data["upload_log"])

        resolved_for_company: ResolvedReferences = {
            "company_id": company_id,
            "sector_id": sector_id,
            "country_id": country_id,
            "currency_id": currency_id,
            "segmentation_criteria_id": segmentation_criteria_id,
            "rating_methodology_ids": rating_methodology_ids,
            "industry_risk_type_ids": industry_risk_type_ids,
            "upload_id": upload_id,
            "company_surrogate_key": 0,
            "snapshot_id": 0,
        }

        company_insert_payload = build_insert_ready_data(
            db_ready_data, resolved_for_company
        )["company"]
        company_surrogate_key = _upsert_company_current(db, company_insert_payload)

        resolved_for_snapshot: ResolvedReferences = {
            **resolved_for_company,
            "company_surrogate_key": company_surrogate_key,
        }
        snapshot_insert_payload = build_insert_ready_data(
            db_ready_data, resolved_for_snapshot
        )["snapshot"]
        snapshot_id = _insert_snapshot(db, snapshot_insert_payload)

        resolved_final: ResolvedReferences = {
            **resolved_for_snapshot,
            "snapshot_id": snapshot_id,
        }
        insert_ready_data = build_insert_ready_data(db_ready_data, resolved_final)

        for row in insert_ready_data["bridge_research_methodologies"]:
            db.add(models.CompanySnapshotResearchMethodology(**row))

        seen_risk_ids: set[int] = set()
        for row in insert_ready_data["bridge_industry_risks"]:
            if row["industry_risk_type_id"] in seen_risk_ids:
                raise ValueError(
                    f"Duplicate industry risk type for snapshot: {row['industry_risk_type_id']}"
                )
            seen_risk_ids.add(row["industry_risk_type_id"])
            db.add(models.CompanySnapshotIndustryRisk(**row))

        seen_metric_years: set[str] = set()
        for row in insert_ready_data["scope_credit_metrics"]:
            if row["metric_year"] in seen_metric_years:
                raise ValueError(
                    f"Duplicate metric_year for snapshot payload: {row['metric_year']}"
                )
            seen_metric_years.add(row["metric_year"])
            db.add(models.ScopeCreditMetric(**row))

    return {
        "upload_id": upload_id,
        "company_id": company_id,
        "company_surrogate_key": company_surrogate_key,
        "snapshot_id": snapshot_id,
    }
