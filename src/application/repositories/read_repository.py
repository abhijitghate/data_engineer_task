from datetime import date
from pathlib import Path

from sqlalchemy import and_, bindparam, column, func, select, table
from sqlalchemy.orm import Session

from src.database import models


v_company_current_metadata = table(
    "v_company_current_metadata",
    column("company_id"),
    column("company_version_id"),
    column("company_name"),
    column("sector_name"),
    column("country_name"),
    column("currency_code"),
    column("accounting_principles"),
    column("end_of_business_month"),
    column("company_valid_from"),
    column("company_valid_to"),
    column("is_current_company_version"),
    schema="applicationdatabase",
)

v_company_versions = table(
    "v_company_versions",
    column("company_id"),
    column("company_version_id"),
    column("company_name"),
    column("sector_name"),
    column("country_name"),
    column("currency_code"),
    column("accounting_principles"),
    column("end_of_business_month"),
    column("company_valid_from"),
    column("company_valid_to"),
    column("is_current_company_version"),
    column("first_snapshot_at"),
    column("last_snapshot_at"),
    column("snapshot_count"),
    schema="applicationdatabase",
)

v_company_snapshots_enriched = table(
    "v_company_snapshots_enriched",
    column("snapshot_id"),
    column("upload_id"),
    column("file_name"),
    column("storage_path"),
    column("discussion_version"),
    column("uploaded_at"),
    column("upload_status"),
    column("company_id"),
    column("company_version_id"),
    column("company_name"),
    column("sector_name"),
    column("country_name"),
    column("currency_code"),
    column("accounting_principles"),
    column("end_of_business_month"),
    column("segmentation_criteria_name"),
    column("business_risk_profile"),
    column("blended_industry_risk_profile"),
    column("competitive_positioning"),
    column("market_share"),
    column("diversification"),
    column("operating_profitability"),
    column("sector_or_company_specific_factor_1"),
    column("sector_or_company_specific_factor_2"),
    column("financial_risk_profile"),
    column("leverage"),
    column("interest_cover"),
    column("cash_flow_cover"),
    column("liquidity_assessment"),
    column("snapshot_ingested_at"),
    column("snapshot_valid_from"),
    column("snapshot_valid_to"),
    column("snapshot_status"),
    schema="applicationdatabase",
)

v_company_metric_history = table(
    "v_company_metric_history",
    column("snapshot_id"),
    column("upload_id"),
    column("company_id"),
    column("company_version_id"),
    column("company_name"),
    column("sector_name"),
    column("country_name"),
    column("currency_code"),
    column("discussion_version"),
    column("snapshot_ingested_at"),
    column("metric_year"),
    column("scope_adjusted_ebitda_interest_cover"),
    column("scope_adjusted_ebitda_interest_cover_status"),
    column("scope_adjusted_debt_ebitda"),
    column("scope_adjusted_debt_ebitda_status"),
    column("scope_adjusted_ffo_debt"),
    column("scope_adjusted_ffo_debt_status"),
    column("scope_adjusted_loan_value"),
    column("scope_adjusted_loan_value_status"),
    column("scope_adjusted_focf_debt"),
    column("scope_adjusted_focf_debt_status"),
    column("liquidity"),
    column("liquidity_status"),
    schema="applicationdatabase",
)

v_upload_stats = table(
    "v_upload_stats",
    column("upload_id"),
    column("file_name"),
    column("storage_path"),
    column("discussion_version"),
    column("uploaded_at"),
    column("upload_status"),
    column("file_checksum"),
    column("snapshot_count"),
    column("company_count"),
    column("metric_row_count"),
    column("first_snapshot_at"),
    column("last_snapshot_at"),
    schema="applicationdatabase",
)

upload_logs = models.UploadLog.__table__


class ReadRepository:
    def __init__(self, db: Session):
        self.db = db

    def _fetch_all(self, stmt, params: dict | None = None) -> list[dict]:
        result = self.db.execute(stmt, params or {})
        return [dict(row) for row in result.mappings().all()]

    def _fetch_one(self, stmt, params: dict | None = None) -> dict | None:
        result = self.db.execute(stmt, params or {})
        row = result.mappings().first()
        return dict(row) if row else None

    def list_current_companies(self) -> list[dict]:
        stmt = select(v_company_current_metadata).order_by(
            v_company_current_metadata.c.company_name
        )
        return self._fetch_all(stmt)

    def get_company_latest(self, company_id: int) -> dict | None:
        stmt = (
            select(v_company_snapshots_enriched)
            .where(v_company_snapshots_enriched.c.company_id == company_id)
            .order_by(
                v_company_snapshots_enriched.c.snapshot_ingested_at.desc(),
                v_company_snapshots_enriched.c.snapshot_id.desc(),
            )
            .limit(1)
        )
        return self._fetch_one(stmt)

    def get_company_versions(self, company_id: int) -> list[dict]:
        stmt = (
            select(v_company_versions)
            .where(v_company_versions.c.company_id == company_id)
            .order_by(
                v_company_versions.c.company_valid_from.desc(),
                v_company_versions.c.company_version_id.desc(),
            )
        )
        return self._fetch_all(stmt)

    def get_company_history(self, company_id: int) -> list[dict]:
        stmt = (
            select(v_company_metric_history)
            .where(v_company_metric_history.c.company_id == company_id)
            .order_by(
                v_company_metric_history.c.snapshot_ingested_at.desc(),
                v_company_metric_history.c.metric_year.desc(),
            )
        )
        return self._fetch_all(stmt)

    def compare_companies_as_of(self, company_ids: list[int], as_of_date: date) -> list[dict]:
        ranked = (
            select(
                v_company_snapshots_enriched.c.company_id,
                v_company_snapshots_enriched.c.company_version_id,
                v_company_snapshots_enriched.c.company_name,
                v_company_snapshots_enriched.c.sector_name,
                v_company_snapshots_enriched.c.country_name,
                v_company_snapshots_enriched.c.currency_code,
                v_company_snapshots_enriched.c.snapshot_id.label("as_of_snapshot_id"),
                v_company_snapshots_enriched.c.snapshot_ingested_at.label(
                    "as_of_snapshot_ingested_at"
                ),
                v_company_snapshots_enriched.c.discussion_version,
                func.row_number()
                .over(
                    partition_by=v_company_snapshots_enriched.c.company_id,
                    order_by=[
                        v_company_snapshots_enriched.c.snapshot_ingested_at.desc(),
                        v_company_snapshots_enriched.c.snapshot_id.desc(),
                    ],
                )
                .label("rn"),
            )
            .where(
                and_(
                    v_company_snapshots_enriched.c.company_id.in_(
                        bindparam("company_ids", expanding=True)
                    ),
                    func.date(v_company_snapshots_enriched.c.snapshot_ingested_at)
                    <= bindparam("as_of_date"),
                )
            )
            .subquery("ranked")
        )

        stmt = (
            select(
                ranked.c.company_id,
                ranked.c.company_version_id,
                ranked.c.company_name,
                ranked.c.sector_name,
                ranked.c.country_name,
                ranked.c.currency_code,
                ranked.c.as_of_snapshot_id,
                ranked.c.as_of_snapshot_ingested_at,
                ranked.c.discussion_version,
            )
            .where(ranked.c.rn == 1)
            .order_by(ranked.c.company_id)
        )
        return self._fetch_all(stmt, {"company_ids": company_ids, "as_of_date": as_of_date})

    def list_snapshots(
        self,
        company_id: int | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        sector: str | None = None,
        country: str | None = None,
        currency: str | None = None,
    ) -> list[dict]:
        clauses = []

        if company_id is not None:
            clauses.append(v_company_snapshots_enriched.c.company_id == company_id)
        if from_date is not None:
            clauses.append(func.date(v_company_snapshots_enriched.c.snapshot_ingested_at) >= from_date)
        if to_date is not None:
            clauses.append(func.date(v_company_snapshots_enriched.c.snapshot_ingested_at) <= to_date)
        if sector is not None:
            clauses.append(v_company_snapshots_enriched.c.sector_name == sector)
        if country is not None:
            clauses.append(v_company_snapshots_enriched.c.country_name == country)
        if currency is not None:
            clauses.append(v_company_snapshots_enriched.c.currency_code == currency)

        stmt = select(v_company_snapshots_enriched)
        if clauses:
            stmt = stmt.where(and_(*clauses))
        stmt = stmt.order_by(
            v_company_snapshots_enriched.c.snapshot_ingested_at.desc(),
            v_company_snapshots_enriched.c.snapshot_id.desc(),
        )
        return self._fetch_all(stmt)

    def get_snapshot(self, snapshot_id: int) -> dict | None:
        stmt = select(v_company_snapshots_enriched).where(
            v_company_snapshots_enriched.c.snapshot_id == snapshot_id
        )
        return self._fetch_one(stmt)

    def get_latest_snapshots(self) -> list[dict]:
        ranked = (
            select(
                v_company_snapshots_enriched,
                func.row_number()
                .over(
                    partition_by=v_company_snapshots_enriched.c.company_id,
                    order_by=[
                        v_company_snapshots_enriched.c.snapshot_ingested_at.desc(),
                        v_company_snapshots_enriched.c.snapshot_id.desc(),
                    ],
                )
                .label("rn"),
            )
            .subquery("ranked")
        )
        stmt = (
            select(*[ranked.c[col.name] for col in v_company_snapshots_enriched.c])
            .where(ranked.c.rn == 1)
            .order_by(ranked.c.company_id)
        )
        return self._fetch_all(stmt)

    def list_uploads(self) -> list[dict]:
        stmt = (
            select(
                upload_logs.c.upload_id,
                upload_logs.c.file_name,
                upload_logs.c.storage_path,
                upload_logs.c.discussion_version,
                upload_logs.c.uploaded_at,
                upload_logs.c.upload_status,
                upload_logs.c.file_checksum,
            )
            .order_by(upload_logs.c.uploaded_at.desc(), upload_logs.c.upload_id.desc())
        )
        return self._fetch_all(stmt)

    def get_upload(self, upload_id: int) -> dict | None:
        stmt = select(
            upload_logs.c.upload_id,
            upload_logs.c.file_name,
            upload_logs.c.storage_path,
            upload_logs.c.discussion_version,
            upload_logs.c.uploaded_at,
            upload_logs.c.upload_status,
            upload_logs.c.file_checksum,
        ).where(upload_logs.c.upload_id == upload_id)
        return self._fetch_one(stmt)

    def list_upload_stats(self) -> list[dict]:
        stmt = select(v_upload_stats).order_by(
            v_upload_stats.c.uploaded_at.desc(), v_upload_stats.c.upload_id.desc()
        )
        return self._fetch_all(stmt)

    def get_upload_snapshots(self, upload_id: int) -> list[dict]:
        stmt = (
            select(v_company_snapshots_enriched)
            .where(v_company_snapshots_enriched.c.upload_id == upload_id)
            .order_by(
                v_company_snapshots_enriched.c.snapshot_ingested_at.desc(),
                v_company_snapshots_enriched.c.snapshot_id.desc(),
            )
        )
        return self._fetch_all(stmt)

    def get_upload_file_path(self, upload_id: int) -> Path | None:
        stmt = select(upload_logs.c.storage_path).where(upload_logs.c.upload_id == upload_id)
        row = self._fetch_one(stmt)
        if row is None or row.get("storage_path") is None:
            return None
        return Path(row["storage_path"])
