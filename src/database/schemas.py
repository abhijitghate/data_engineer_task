
from typing import Literal, Optional

from pydantic import BaseModel, Field

MetricStatus = Literal["numeric", "no_data", "locked", "missing", "invalid"]


class IndustryRiskSchema(BaseModel):
    industry_risk_name: str
    industry_risk_score: str
    industry_weight: float = Field(ge=0, le=1)


class SegmentationCriteriaSchema(BaseModel):
    segmentation_criteria_name: str

class CurrencySchema(BaseModel):
    currency_code: str

class CountrySchema(BaseModel):
    country_name: str

class RatingMethodologyAppliedSchema(BaseModel):
    rating_methodology_applied_name: str

class SectorSchema(BaseModel):
    sector_name: str

class ScopeCreditMetricSchema(BaseModel):
    # Must align with DB check constraints in fact_scope_credit_metrics.
    scope_adjusted_ebitda_interest_cover: float | None
    scope_adjusted_ebitda_interest_cover_status: MetricStatus
    scope_adjusted_debt_ebitda: float | None
    scope_adjusted_debt_ebitda_status: MetricStatus
    scope_adjusted_ffo_debt: float | None
    scope_adjusted_ffo_debt_status: MetricStatus
    scope_adjusted_loan_value: float | None
    scope_adjusted_loan_value_status: MetricStatus
    scope_adjusted_focf_debt: float | None
    scope_adjusted_focf_debt_status: MetricStatus
    liquidity: float | None
    liquidity_status: MetricStatus
    metric_year: str



class IngestionSchema(BaseModel):
    # Upload metadata for audit/idempotency in warehouse.upload_logs.
    file_name: str
    storage_path: str
    discussion_version: str
    file_checksum: str

    company_name: str
    sector: SectorSchema
    rating_methodology_applied: list[RatingMethodologyAppliedSchema]
    industry_risks: list[IndustryRiskSchema]
    segmentation_criteria: SegmentationCriteriaSchema
    reporting_currency: CurrencySchema
    country_of_origin: CountrySchema
    accounting_principles: str
    end_of_business_month: str
    business_risk_profile: str
    blended_industry_risk_profile: str
    competitive_positioning: str
    market_share: str
    diversification: str
    operating_profitability: str
    sector_or_company_specific_factor_1: str
    sector_or_company_specific_factor_2: Optional[str]
    financial_risk_profile: str
    leverage: str
    interest_cover: str
    cash_flow_cover: str
    liquidity_assessment: str
    scope_credit_metrics: list[ScopeCreditMetricSchema]
