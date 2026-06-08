from typing import TypedDict

import src.database.schemas as schema


class UploadLogPayload(TypedDict):
    file_name: str
    storage_path: str
    discussion_version: str
    file_checksum: str
    upload_status: str


class DimensionsPayload(TypedDict):
    sector_name: str
    country_name: str
    currency_code: str
    segmentation_criteria_name: str
    rating_methodology_applied_names: list[str]
    industry_risk_type_names: list[str]


class CompanyNaturalPayload(TypedDict):
    company_name: str
    accounting_principles: str
    end_of_business_month: str
    sector_name: str
    country_name: str
    currency_code: str


class SnapshotNaturalPayload(TypedDict):
    snapshot_status: str
    segmentation_criteria_name: str
    business_risk_profile: str
    blended_industry_risk_profile: str
    competitive_positioning: str
    market_share: str
    diversification: str
    operating_profitability: str
    sector_or_company_specific_factor_1: str
    sector_or_company_specific_factor_2: str | None
    financial_risk_profile: str
    leverage: str
    interest_cover: str
    cash_flow_cover: str
    liquidity_assessment: str


class IndustryRiskNaturalPayload(TypedDict):
    industry_risk_name: str
    industry_risk_score: str
    industry_weight: float


class BridgesNaturalPayload(TypedDict):
    research_methodologies: list[str]
    industry_risks: list[IndustryRiskNaturalPayload]


class ScopeCreditMetricNaturalPayload(TypedDict):
    metric_year: str
    scope_adjusted_ebitda_interest_cover: float | None
    scope_adjusted_ebitda_interest_cover_status: schema.MetricStatus
    scope_adjusted_debt_ebitda: float | None
    scope_adjusted_debt_ebitda_status: schema.MetricStatus
    scope_adjusted_ffo_debt: float | None
    scope_adjusted_ffo_debt_status: schema.MetricStatus
    scope_adjusted_loan_value: float | None
    scope_adjusted_loan_value_status: schema.MetricStatus
    scope_adjusted_focf_debt: float | None
    scope_adjusted_focf_debt_status: schema.MetricStatus
    liquidity: float | None
    liquidity_status: schema.MetricStatus


class DBReadyData(TypedDict):
    upload_log: UploadLogPayload
    dimensions: DimensionsPayload
    company: CompanyNaturalPayload
    snapshot: SnapshotNaturalPayload
    bridges: BridgesNaturalPayload
    scope_credit_metrics: list[ScopeCreditMetricNaturalPayload]


class ResolvedReferences(TypedDict):
    # Application-level company id (dimension_companies.company_id)
    company_id: int

    # Dimension FK ids resolved from natural keys.
    sector_id: int
    country_id: int
    currency_id: int
    segmentation_criteria_id: int
    rating_methodology_ids: dict[str, int]
    industry_risk_type_ids: dict[str, int]

    # IDs produced by inserts earlier in the same transaction.
    upload_id: int
    company_version_id: int
    snapshot_id: int


class CompanyInsertPayload(TypedDict):
    company_id: int
    company_name: str
    sector_id: int
    country_id: int
    currency_id: int
    accounting_principles: str
    end_of_business_month: str


class SnapshotInsertPayload(TypedDict):
    upload_id: int
    company_version_id: int
    snapshot_status: str
    segmentation_criteria_id: int
    business_risk_profile: str
    blended_industry_risk_profile: str
    competitive_positioning: str
    market_share: str
    diversification: str
    operating_profitability: str
    sector_or_company_specific_factor_1: str
    sector_or_company_specific_factor_2: str | None
    financial_risk_profile: str
    leverage: str
    interest_cover: str
    cash_flow_cover: str
    liquidity_assessment: str


class ResearchMethodologyBridgeInsertPayload(TypedDict):
    snapshot_id: int
    rating_methodology_applied_id: int


class IndustryRiskBridgeInsertPayload(TypedDict):
    snapshot_id: int
    industry_risk_type_id: int
    industry_risk_score: str
    industry_weight: float


class ScopeCreditMetricInsertPayload(TypedDict):
    snapshot_id: int
    metric_year: str
    scope_adjusted_ebitda_interest_cover: float | None
    scope_adjusted_ebitda_interest_cover_status: schema.MetricStatus
    scope_adjusted_debt_ebitda: float | None
    scope_adjusted_debt_ebitda_status: schema.MetricStatus
    scope_adjusted_ffo_debt: float | None
    scope_adjusted_ffo_debt_status: schema.MetricStatus
    scope_adjusted_loan_value: float | None
    scope_adjusted_loan_value_status: schema.MetricStatus
    scope_adjusted_focf_debt: float | None
    scope_adjusted_focf_debt_status: schema.MetricStatus
    liquidity: float | None
    liquidity_status: schema.MetricStatus


class InsertReadyData(TypedDict):
    upload_log: UploadLogPayload
    company: CompanyInsertPayload
    snapshot: SnapshotInsertPayload
    bridge_research_methodologies: list[ResearchMethodologyBridgeInsertPayload]
    bridge_industry_risks: list[IndustryRiskBridgeInsertPayload]
    scope_credit_metrics: list[ScopeCreditMetricInsertPayload]


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def transform_to_db_ready(validated_data: schema.IngestionSchema) -> DBReadyData:
    rating_methodologies = _unique_preserve_order(
        [
            item.rating_methodology_applied_name
            for item in validated_data.rating_methodology_applied
        ]
    )
    industry_risk_types = _unique_preserve_order(
        [item.industry_risk_name for item in validated_data.industry_risks]
    )

    return DBReadyData(
        upload_log=UploadLogPayload(
            file_name=validated_data.file_name,
            storage_path=validated_data.storage_path,
            discussion_version=validated_data.discussion_version,
            file_checksum=validated_data.file_checksum,
            upload_status="success",
        ),
        dimensions=DimensionsPayload(
            sector_name=validated_data.sector.sector_name,
            country_name=validated_data.country_of_origin.country_name,
            currency_code=validated_data.reporting_currency.currency_code,
            segmentation_criteria_name=(
                validated_data.segmentation_criteria.segmentation_criteria_name
            ),
            rating_methodology_applied_names=rating_methodologies,
            industry_risk_type_names=industry_risk_types,
        ),
        company=CompanyNaturalPayload(
            company_name=validated_data.company_name,
            accounting_principles=validated_data.accounting_principles,
            end_of_business_month=validated_data.end_of_business_month,
            sector_name=validated_data.sector.sector_name,
            country_name=validated_data.country_of_origin.country_name,
            currency_code=validated_data.reporting_currency.currency_code,
        ),
        snapshot=SnapshotNaturalPayload(
            snapshot_status="success",
            segmentation_criteria_name=(
                validated_data.segmentation_criteria.segmentation_criteria_name
            ),
            business_risk_profile=validated_data.business_risk_profile,
            blended_industry_risk_profile=validated_data.blended_industry_risk_profile,
            competitive_positioning=validated_data.competitive_positioning,
            market_share=validated_data.market_share,
            diversification=validated_data.diversification,
            operating_profitability=validated_data.operating_profitability,
            sector_or_company_specific_factor_1=(
                validated_data.sector_or_company_specific_factor_1
            ),
            sector_or_company_specific_factor_2=(
                validated_data.sector_or_company_specific_factor_2
            ),
            financial_risk_profile=validated_data.financial_risk_profile,
            leverage=validated_data.leverage,
            interest_cover=validated_data.interest_cover,
            cash_flow_cover=validated_data.cash_flow_cover,
            liquidity_assessment=validated_data.liquidity_assessment,
        ),
        bridges=BridgesNaturalPayload(
            research_methodologies=rating_methodologies,
            industry_risks=[
                IndustryRiskNaturalPayload(
                    industry_risk_name=item.industry_risk_name,
                    industry_risk_score=item.industry_risk_score,
                    industry_weight=item.industry_weight,
                )
                for item in validated_data.industry_risks
            ],
        ),
        scope_credit_metrics=[
            ScopeCreditMetricNaturalPayload(
                metric_year=item.metric_year,
                scope_adjusted_ebitda_interest_cover=(
                    item.scope_adjusted_ebitda_interest_cover
                ),
                scope_adjusted_ebitda_interest_cover_status=(
                    item.scope_adjusted_ebitda_interest_cover_status
                ),
                scope_adjusted_debt_ebitda=item.scope_adjusted_debt_ebitda,
                scope_adjusted_debt_ebitda_status=item.scope_adjusted_debt_ebitda_status,
                scope_adjusted_ffo_debt=item.scope_adjusted_ffo_debt,
                scope_adjusted_ffo_debt_status=item.scope_adjusted_ffo_debt_status,
                scope_adjusted_loan_value=item.scope_adjusted_loan_value,
                scope_adjusted_loan_value_status=item.scope_adjusted_loan_value_status,
                scope_adjusted_focf_debt=item.scope_adjusted_focf_debt,
                scope_adjusted_focf_debt_status=item.scope_adjusted_focf_debt_status,
                liquidity=item.liquidity,
                liquidity_status=item.liquidity_status,
            )
            for item in validated_data.scope_credit_metrics
        ],
    )


def _require_mapping_value(mapping: dict[str, int], key: str, mapping_name: str) -> int:
    if key not in mapping:
        raise KeyError(f"Missing {mapping_name} id for key: {key}")
    return mapping[key]


def build_insert_ready_data(
    db_ready_data: DBReadyData, resolved_references: ResolvedReferences
) -> InsertReadyData:
    bridge_research_methodologies: list[ResearchMethodologyBridgeInsertPayload] = []
    for name in db_ready_data["bridges"]["research_methodologies"]:
        bridge_research_methodologies.append(
            ResearchMethodologyBridgeInsertPayload(
                snapshot_id=resolved_references["snapshot_id"],
                rating_methodology_applied_id=_require_mapping_value(
                    resolved_references["rating_methodology_ids"],
                    name,
                    "rating_methodology",
                ),
            )
        )

    bridge_industry_risks: list[IndustryRiskBridgeInsertPayload] = []
    for risk in db_ready_data["bridges"]["industry_risks"]:
        bridge_industry_risks.append(
            IndustryRiskBridgeInsertPayload(
                snapshot_id=resolved_references["snapshot_id"],
                industry_risk_type_id=_require_mapping_value(
                    resolved_references["industry_risk_type_ids"],
                    risk["industry_risk_name"],
                    "industry_risk_type",
                ),
                industry_risk_score=risk["industry_risk_score"],
                industry_weight=risk["industry_weight"],
            )
        )

    scope_credit_metrics: list[ScopeCreditMetricInsertPayload] = []
    for metric in db_ready_data["scope_credit_metrics"]:
        scope_credit_metrics.append(
            ScopeCreditMetricInsertPayload(
                snapshot_id=resolved_references["snapshot_id"],
                metric_year=metric["metric_year"],
                scope_adjusted_ebitda_interest_cover=metric[
                    "scope_adjusted_ebitda_interest_cover"
                ],
                scope_adjusted_ebitda_interest_cover_status=metric[
                    "scope_adjusted_ebitda_interest_cover_status"
                ],
                scope_adjusted_debt_ebitda=metric["scope_adjusted_debt_ebitda"],
                scope_adjusted_debt_ebitda_status=metric[
                    "scope_adjusted_debt_ebitda_status"
                ],
                scope_adjusted_ffo_debt=metric["scope_adjusted_ffo_debt"],
                scope_adjusted_ffo_debt_status=metric["scope_adjusted_ffo_debt_status"],
                scope_adjusted_loan_value=metric["scope_adjusted_loan_value"],
                scope_adjusted_loan_value_status=metric[
                    "scope_adjusted_loan_value_status"
                ],
                scope_adjusted_focf_debt=metric["scope_adjusted_focf_debt"],
                scope_adjusted_focf_debt_status=metric[
                    "scope_adjusted_focf_debt_status"
                ],
                liquidity=metric["liquidity"],
                liquidity_status=metric["liquidity_status"],
            )
        )

    return InsertReadyData(
        upload_log=db_ready_data["upload_log"],
        company=CompanyInsertPayload(
            company_id=resolved_references["company_id"],
            company_name=db_ready_data["company"]["company_name"],
            sector_id=resolved_references["sector_id"],
            country_id=resolved_references["country_id"],
            currency_id=resolved_references["currency_id"],
            accounting_principles=db_ready_data["company"]["accounting_principles"],
            end_of_business_month=db_ready_data["company"]["end_of_business_month"],
        ),
        snapshot=SnapshotInsertPayload(
            upload_id=resolved_references["upload_id"],
            company_version_id=resolved_references["company_version_id"],
            snapshot_status=db_ready_data["snapshot"]["snapshot_status"],
            segmentation_criteria_id=resolved_references["segmentation_criteria_id"],
            business_risk_profile=db_ready_data["snapshot"]["business_risk_profile"],
            blended_industry_risk_profile=db_ready_data["snapshot"][
                "blended_industry_risk_profile"
            ],
            competitive_positioning=db_ready_data["snapshot"]["competitive_positioning"],
            market_share=db_ready_data["snapshot"]["market_share"],
            diversification=db_ready_data["snapshot"]["diversification"],
            operating_profitability=db_ready_data["snapshot"]["operating_profitability"],
            sector_or_company_specific_factor_1=db_ready_data["snapshot"][
                "sector_or_company_specific_factor_1"
            ],
            sector_or_company_specific_factor_2=db_ready_data["snapshot"][
                "sector_or_company_specific_factor_2"
            ],
            financial_risk_profile=db_ready_data["snapshot"]["financial_risk_profile"],
            leverage=db_ready_data["snapshot"]["leverage"],
            interest_cover=db_ready_data["snapshot"]["interest_cover"],
            cash_flow_cover=db_ready_data["snapshot"]["cash_flow_cover"],
            liquidity_assessment=db_ready_data["snapshot"]["liquidity_assessment"],
        ),
        bridge_research_methodologies=bridge_research_methodologies,
        bridge_industry_risks=bridge_industry_risks,
        scope_credit_metrics=scope_credit_metrics,
    )
