
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    CheckConstraint,
    text,
)
from datetime import datetime
from sqlalchemy.orm import relationship
from .database import Base

class UploadLog(Base):
    __tablename__ = "upload_logs"
    __table_args__ = {"schema": "warehouse"}

    upload_id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    discussion_version = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True),server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    upload_status = Column(String, server_default=text("'success'"), nullable=False)
    file_checksum = Column(String, unique=True, nullable=False)
    snapshots = relationship("CompanySnapshot", back_populates="upload_log")

class Sector(Base):
    __tablename__ = "dimension_sectors"
    __table_args__ = {"schema": "warehouse"}

    sector_id = Column(Integer, primary_key=True, index=True)
    sector_name = Column(String, unique=True, nullable=False)
    companies = relationship("Company", back_populates="sector")

class Country(Base):
    __tablename__ = "dimension_countries"
    __table_args__ = {"schema": "warehouse"}

    country_id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String, unique=True, nullable=False)
    companies = relationship("Company", back_populates="country")


class Currency(Base):
    __tablename__ = "dimension_currencies"
    __table_args__ = {"schema": "warehouse"}

    currency_id = Column(Integer, primary_key=True, index=True)
    currency_code = Column(String, unique=True, nullable=False)
    companies = relationship("Company", back_populates="currency")


class RatingMethodologyApplied(Base):
    __tablename__ = "dimension_rating_methodologies_applied"
    __table_args__ = {"schema": "warehouse"}

    rating_methodology_applied_id = Column(Integer, primary_key=True, index=True)
    rating_methodology_applied_name = Column(String, unique=True, nullable=False)
    snapshot_links = relationship(
        "CompanySnapshotResearchMethodology", back_populates="rating_methodology"
    )


class SegmentationCriteria(Base):
    __tablename__ = "dimension_segmentation_criteria"
    __table_args__ = {"schema": "warehouse"}

    segmentation_criteria_id = Column(Integer, primary_key=True, index=True)
    segmentation_criteria_name = Column(String, unique=True, nullable=False)
    snapshots = relationship("CompanySnapshot", back_populates="segmentation_criteria")


class IndustryRiskType(Base):
    __tablename__ = "dimension_industry_risk_types"
    __table_args__ = {"schema": "warehouse"}

    industry_risk_type_id = Column(Integer, primary_key=True, index=True)
    industry_risk_type_name = Column(String, unique=True, nullable=False)
    snapshot_links = relationship(
        "CompanySnapshotIndustryRisk", back_populates="industry_risk_type"
    )


class Company(Base):
    __tablename__ = "dimension_companies"
    __table_args__ = {"schema": "warehouse"}

    company_version_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False, index=True)
    company_name = Column(String, nullable=False)
    sector_id = Column(
        Integer,
        ForeignKey("warehouse.dimension_sectors.sector_id"),
        nullable=False,
    )
    country_id = Column(
        Integer,
        ForeignKey("warehouse.dimension_countries.country_id"),
        nullable=False,
    )
    currency_id = Column(
        Integer,
        ForeignKey("warehouse.dimension_currencies.currency_id"),
        nullable=False,
    )
    accounting_principles = Column(String, nullable=False)
    end_of_business_month = Column(String, nullable=False)
    valid_from = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    valid_to = Column(
        DateTime(timezone=True),
        server_default=text("'infinity'"),
        nullable=False,
    )
    is_current = Column(Boolean, server_default=text("TRUE"), nullable=False)
    sector = relationship("Sector", back_populates="companies")
    country = relationship("Country", back_populates="companies")
    currency = relationship("Currency", back_populates="companies")
    snapshots = relationship("CompanySnapshot", back_populates="company")


class CompanySnapshot(Base):
    __tablename__ = "fact_company_snapshots"
    __table_args__ = {"schema": "warehouse"}

    snapshot_id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("warehouse.upload_logs.upload_id"), nullable=False)
    company_version_id = Column(
        Integer,
        ForeignKey("warehouse.dimension_companies.company_version_id"),
        nullable=False,
    )
    ingested_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    snapshot_status = Column(String, server_default=text("'success'"), nullable=False)
    segmentation_criteria_id = Column(
        Integer,
        ForeignKey("warehouse.dimension_segmentation_criteria.segmentation_criteria_id"),
        nullable=False,
    )

    business_risk_profile = Column(String, nullable=False)
    blended_industry_risk_profile = Column(String, nullable=False)
    competitive_positioning = Column(String, nullable=False)
    market_share = Column(String, nullable=False)
    diversification = Column(String, nullable=False)
    operating_profitability = Column(String, nullable=False)
    sector_or_company_specific_factor_1 = Column(String)
    sector_or_company_specific_factor_2 = Column(String)

    financial_risk_profile = Column(String, nullable=False)
    leverage = Column(String, nullable=False)
    interest_cover = Column(String, nullable=False)
    cash_flow_cover = Column(String, nullable=False)
    liquidity_assessment = Column(String, nullable=False)

    valid_from = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    valid_to = Column(
        DateTime(timezone=True),
        server_default=text("'infinity'"),
        nullable=False,
    )
    upload_log = relationship("UploadLog", back_populates="snapshots")
    company = relationship("Company", back_populates="snapshots")
    segmentation_criteria = relationship(
        "SegmentationCriteria", back_populates="snapshots"
    )
    research_methodologies = relationship(
        "CompanySnapshotResearchMethodology", back_populates="snapshot"
    )
    industry_risks = relationship(
        "CompanySnapshotIndustryRisk", back_populates="snapshot"
    )
    scope_credit_metrics = relationship("ScopeCreditMetric", back_populates="snapshot")


class CompanySnapshotResearchMethodology(Base):
    __tablename__ = "bridge_company_snapshot_research_methodology"
    __table_args__ = {"schema": "warehouse"}

    snapshot_id = Column(
        Integer,
        ForeignKey("warehouse.fact_company_snapshots.snapshot_id"),
        primary_key=True,
        nullable=False,
    )
    rating_methodology_applied_id = Column(
        Integer,
        ForeignKey(
            "warehouse.dimension_rating_methodologies_applied.rating_methodology_applied_id"
        ),
        primary_key=True,
        nullable=False,
    )
    snapshot = relationship("CompanySnapshot", back_populates="research_methodologies")
    rating_methodology = relationship(
        "RatingMethodologyApplied", back_populates="snapshot_links"
    )


class CompanySnapshotIndustryRisk(Base):
    __tablename__ = "bridge_company_snapshot_industry_risks"
    __table_args__ = {"schema": "warehouse"}

    snapshot_id = Column(
        Integer,
        ForeignKey("warehouse.fact_company_snapshots.snapshot_id"),
        primary_key=True,
        nullable=False,
    )
    industry_risk_type_id = Column(
        Integer,
        ForeignKey("warehouse.dimension_industry_risk_types.industry_risk_type_id"),
        primary_key=True,
        nullable=False,
    )
    industry_risk_score = Column(String, nullable=False)
    industry_weight = Column(Numeric(6, 4), nullable=False)
    snapshot = relationship("CompanySnapshot", back_populates="industry_risks")
    industry_risk_type = relationship("IndustryRiskType", back_populates="snapshot_links")


class ScopeCreditMetric(Base):
    __tablename__ = "fact_scope_credit_metrics"
    __table_args__ = (
        UniqueConstraint("snapshot_id", "metric_year", name="uq_metrics_snapshot_year"),
        CheckConstraint(
            "scope_adjusted_ebitda_interest_cover_status IN "
            "('numeric', 'no_data', 'locked', 'missing', 'invalid')",
            name="chk_ebitda_interest_cover_status",
        ),
        CheckConstraint(
            "scope_adjusted_debt_ebitda_status IN "
            "('numeric', 'no_data', 'locked', 'missing', 'invalid')",
            name="chk_debt_ebitda_status",
        ),
        CheckConstraint(
            "scope_adjusted_ffo_debt_status IN "
            "('numeric', 'no_data', 'locked', 'missing', 'invalid')",
            name="chk_ffo_debt_status",
        ),
        CheckConstraint(
            "scope_adjusted_loan_value_status IN "
            "('numeric', 'no_data', 'locked', 'missing', 'invalid')",
            name="chk_loan_value_status",
        ),
        CheckConstraint(
            "scope_adjusted_focf_debt_status IN "
            "('numeric', 'no_data', 'locked', 'missing', 'invalid')",
            name="chk_focf_debt_status",
        ),
        CheckConstraint(
            "liquidity_status IN ('numeric', 'no_data', 'locked', 'missing', 'invalid')",
            name="chk_liquidity_status",
        ),
        {"schema": "warehouse"},
    )

    credit_metric_id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(
        Integer,
        ForeignKey("warehouse.fact_company_snapshots.snapshot_id"),
        nullable=False,
        index=True,
    )
    metric_year = Column(String, nullable=False)

    scope_adjusted_ebitda_interest_cover = Column(Numeric(10, 4))
    scope_adjusted_ebitda_interest_cover_status = Column(
        String, server_default=text("'numeric'"), nullable=False
    )
    scope_adjusted_debt_ebitda = Column(Numeric(10, 4))
    scope_adjusted_debt_ebitda_status = Column(
        String, server_default=text("'numeric'"), nullable=False
    )
    scope_adjusted_ffo_debt = Column(Numeric(10, 4))
    scope_adjusted_ffo_debt_status = Column(
        String, server_default=text("'numeric'"), nullable=False
    )
    scope_adjusted_loan_value = Column(Numeric(10, 4))
    scope_adjusted_loan_value_status = Column(
        String, server_default=text("'numeric'"), nullable=False
    )
    scope_adjusted_focf_debt = Column(Numeric(10, 4))
    scope_adjusted_focf_debt_status = Column(
        String, server_default=text("'numeric'"), nullable=False
    )
    liquidity = Column(Numeric(10, 4))
    liquidity_status = Column(String, server_default=text("'numeric'"), nullable=False)
    snapshot = relationship("CompanySnapshot", back_populates="scope_credit_metrics")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    __table_args__ = {"schema": "warehouse"}

    run_id = Column(Integer, primary_key=True, index=True)
    discussion_version = Column(String, nullable=False)
    started_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, server_default=text("'running'"), nullable=False)
    files_total = Column(Integer, server_default=text("0"), nullable=False)
    files_processed = Column(Integer, server_default=text("0"), nullable=False)
    files_succeeded = Column(Integer, server_default=text("0"), nullable=False)
    files_failed = Column(Integer, server_default=text("0"), nullable=False)
    files_skipped = Column(Integer, server_default=text("0"), nullable=False)
    quality_completeness_avg = Column(Numeric(6, 4), nullable=True)
    quality_validity_avg = Column(Numeric(6, 4), nullable=True)
    quality_warning_count = Column(Integer, server_default=text("0"), nullable=False)
    extract_ms_total = Column(Integer, server_default=text("0"), nullable=False)
    validate_ms_total = Column(Integer, server_default=text("0"), nullable=False)
    transform_ms_total = Column(Integer, server_default=text("0"), nullable=False)
    load_ms_total = Column(Integer, server_default=text("0"), nullable=False)
    duration_ms = Column(Integer, nullable=True)
    error_summary = Column(String, nullable=True)
    processed_files = relationship("ProcessedFile", back_populates="run")


class ProcessedFile(Base):
    __tablename__ = "processed_files"
    __table_args__ = {"schema": "warehouse"}

    processed_file_id = Column(Integer, primary_key=True, index=True)
    run_id = Column(
        Integer,
        ForeignKey("warehouse.pipeline_runs.run_id"),
        nullable=False,
        index=True,
    )
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_checksum = Column(String, nullable=False, index=True)
    discussion_version = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    upload_id = Column(Integer, nullable=True)
    company_id = Column(Integer, nullable=True)
    company_version_id = Column(Integer, nullable=True)
    snapshot_id = Column(Integer, nullable=True)
    quality_completeness_rate = Column(Numeric(6, 4), nullable=True)
    quality_validity_rate = Column(Numeric(6, 4), nullable=True)
    quality_warning_count = Column(Integer, nullable=True)
    quality_warnings = Column(String, nullable=True)
    extract_ms = Column(Integer, nullable=True)
    validate_ms = Column(Integer, nullable=True)
    transform_ms = Column(Integer, nullable=True)
    load_ms = Column(Integer, nullable=True)
    total_ms = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)
    processed_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    run = relationship("PipelineRun", back_populates="processed_files")
    validation_findings = relationship(
        "ValidationFinding", back_populates="processed_file"
    )


class ValidationFinding(Base):
    __tablename__ = "validation_findings"
    __table_args__ = {"schema": "warehouse"}

    validation_finding_id = Column(Integer, primary_key=True, index=True)
    processed_file_id = Column(
        Integer,
        ForeignKey("warehouse.processed_files.processed_file_id"),
        nullable=False,
        index=True,
    )
    run_id = Column(Integer, nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_checksum = Column(String, nullable=False, index=True)
    discussion_version = Column(String, nullable=False, index=True)
    rule_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    field_name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    processed_file = relationship("ProcessedFile", back_populates="validation_findings")
