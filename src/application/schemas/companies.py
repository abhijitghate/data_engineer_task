from datetime import datetime

from pydantic import BaseModel


class CompanyCurrentResponse(BaseModel):
    company_id: int
    company_version_id: int
    company_name: str
    sector_name: str
    country_name: str
    currency_code: str
    accounting_principles: str
    end_of_business_month: str
    company_valid_from: datetime
    company_valid_to: datetime
    is_current_company_version: bool


class CompanyVersionResponse(CompanyCurrentResponse):
    first_snapshot_at: datetime | None
    last_snapshot_at: datetime | None
    snapshot_count: int


class CompanyLatestResponse(BaseModel):
    snapshot_id: int
    upload_id: int
    discussion_version: str
    snapshot_ingested_at: datetime
    snapshot_status: str
    company_id: int
    company_version_id: int
    company_name: str
    sector_name: str
    country_name: str
    currency_code: str
    segmentation_criteria_name: str
    business_risk_profile: str
    blended_industry_risk_profile: str
    competitive_positioning: str
    market_share: str
    diversification: str
    operating_profitability: str
    financial_risk_profile: str
    leverage: str
    interest_cover: str
    cash_flow_cover: str
    liquidity_assessment: str


class CompanyHistoryResponse(BaseModel):
    snapshot_id: int
    upload_id: int
    company_id: int
    company_version_id: int
    company_name: str
    discussion_version: str
    snapshot_ingested_at: datetime
    metric_year: str
    scope_adjusted_ebitda_interest_cover: float | None
    scope_adjusted_ebitda_interest_cover_status: str
    scope_adjusted_debt_ebitda: float | None
    scope_adjusted_debt_ebitda_status: str
    scope_adjusted_ffo_debt: float | None
    scope_adjusted_ffo_debt_status: str
    scope_adjusted_loan_value: float | None
    scope_adjusted_loan_value_status: str
    scope_adjusted_focf_debt: float | None
    scope_adjusted_focf_debt_status: str
    liquidity: float | None
    liquidity_status: str


class CompanyCompareResponse(BaseModel):
    company_id: int
    company_version_id: int
    company_name: str
    sector_name: str
    country_name: str
    currency_code: str
    as_of_snapshot_id: int
    as_of_snapshot_ingested_at: datetime
    discussion_version: str
