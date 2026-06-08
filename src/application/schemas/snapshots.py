from datetime import datetime

from pydantic import BaseModel


class SnapshotResponse(BaseModel):
    snapshot_id: int
    upload_id: int
    file_name: str
    storage_path: str
    discussion_version: str
    uploaded_at: datetime
    upload_status: str
    company_id: int
    company_version_id: int
    company_name: str
    sector_name: str
    country_name: str
    currency_code: str
    accounting_principles: str
    end_of_business_month: str
    segmentation_criteria_name: str
    business_risk_profile: str
    blended_industry_risk_profile: str
    competitive_positioning: str
    market_share: str
    diversification: str
    operating_profitability: str
    sector_or_company_specific_factor_1: str | None
    sector_or_company_specific_factor_2: str | None
    financial_risk_profile: str
    leverage: str
    interest_cover: str
    cash_flow_cover: str
    liquidity_assessment: str
    snapshot_ingested_at: datetime
    snapshot_valid_from: datetime
    snapshot_valid_to: datetime
    snapshot_status: str
