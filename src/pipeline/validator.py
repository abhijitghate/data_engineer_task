import hashlib
import math
from typing import Any, TypedDict

import src.database.schemas as schema


class DataQualityReport(TypedDict):
    completeness_rate: float
    validity_rate: float
    warning_count: int
    missing_required_fields: list[str]
    invalid_metric_values: int
    total_metric_values: int
    warnings: list[str]


REQUIRED_FIELDS = [
    "company_name",
    "corporate_sector",
    "reporting_currency",
    "country_of_origin",
    "accounting_principles",
    "end_of_business_month",
    "segmentation_criteria",
]


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _as_text(value: Any) -> str:
    if _is_missing(value):
        return ""
    return str(value).strip()


def _compute_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _metric_with_status(value: Any) -> tuple[float | None, schema.MetricStatus]:
    if _is_missing(value):
        return None, "missing"

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"no data", "n/a", "na"}:
            return None, "no_data"
        if normalized == "locked":
            return None, "locked"
        try:
            return float(value), "numeric"
        except (TypeError, ValueError):
            return None, "invalid"

    try:
        return float(value), "numeric"
    except (TypeError, ValueError):
        return None, "invalid"


def _build_quality_report(
    raw_data: dict,
    metric_statuses: list[schema.MetricStatus],
    industry_weights: list[float],
) -> DataQualityReport:
    missing_required_fields = [
        field_name for field_name in REQUIRED_FIELDS if _is_missing(raw_data.get(field_name))
    ]
    present_required = len(REQUIRED_FIELDS) - len(missing_required_fields)
    completeness_rate = (
        present_required / len(REQUIRED_FIELDS) if REQUIRED_FIELDS else 1.0
    )

    invalid_metric_values = sum(1 for status in metric_statuses if status == "invalid")
    total_metric_values = len(metric_statuses)
    validity_rate = (
        (total_metric_values - invalid_metric_values) / total_metric_values
        if total_metric_values > 0
        else 1.0
    )

    warnings: list[str] = []
    if missing_required_fields:
        warnings.append(
            "Missing required fields: " + ", ".join(sorted(missing_required_fields))
        )
    if industry_weights:
        total_weight = sum(industry_weights)
        if not math.isclose(total_weight, 1.0, rel_tol=1e-3, abs_tol=1e-3):
            warnings.append(
                f"Industry weights sum is {total_weight:.4f} (expected 1.0000)."
            )

    return DataQualityReport(
        completeness_rate=round(completeness_rate, 4),
        validity_rate=round(validity_rate, 4),
        warning_count=len(warnings),
        missing_required_fields=missing_required_fields,
        invalid_metric_values=invalid_metric_values,
        total_metric_values=total_metric_values,
        warnings=warnings,
    )


def validate_data(
    data: dict, version: str, file_path: str
) -> tuple[schema.IngestionSchema, DataQualityReport]:
    try:
        file_name = file_path.split("/")[-1]
        file_checksum = _compute_sha256(file_path)

        scope_credit_metrics = []
        metric_statuses: list[schema.MetricStatus] = []
        for metric in data.get("scope_credit_metrics", []):
            ebitda_interest_cover, ebitda_interest_cover_status = _metric_with_status(
                metric.get("scope_adjusted_ebitda_interest_cover")
            )
            debt_ebitda, debt_ebitda_status = _metric_with_status(
                metric.get("scope_adjusted_debt_ebitda")
            )
            ffo_debt, ffo_debt_status = _metric_with_status(
                metric.get("scope_adjusted_ffo_debt")
            )
            loan_value, loan_value_status = _metric_with_status(
                metric.get("scope_adjusted_loan_value")
            )
            focf_debt, focf_debt_status = _metric_with_status(
                metric.get("scope_adjusted_focf_debt")
            )
            liquidity, liquidity_status = _metric_with_status(metric.get("liquidity"))
            metric_statuses.extend(
                [
                    ebitda_interest_cover_status,
                    debt_ebitda_status,
                    ffo_debt_status,
                    loan_value_status,
                    focf_debt_status,
                    liquidity_status,
                ]
            )

            scope_credit_metrics.append(
                schema.ScopeCreditMetricSchema(
                    scope_adjusted_ebitda_interest_cover=ebitda_interest_cover,
                    scope_adjusted_ebitda_interest_cover_status=ebitda_interest_cover_status,
                    scope_adjusted_debt_ebitda=debt_ebitda,
                    scope_adjusted_debt_ebitda_status=debt_ebitda_status,
                    scope_adjusted_ffo_debt=ffo_debt,
                    scope_adjusted_ffo_debt_status=ffo_debt_status,
                    scope_adjusted_loan_value=loan_value,
                    scope_adjusted_loan_value_status=loan_value_status,
                    scope_adjusted_focf_debt=focf_debt,
                    scope_adjusted_focf_debt_status=focf_debt_status,
                    liquidity=liquidity,
                    liquidity_status=liquidity_status,
                    metric_year=_as_text(metric.get("metric_year")),
                )
            )

        validated_data = schema.IngestionSchema(
            file_name=file_name,
            storage_path=file_path,
            discussion_version=version,
            file_checksum=file_checksum,
            company_name=_as_text(data.get("company_name")),
            sector=schema.SectorSchema(sector_name=_as_text(data.get("corporate_sector"))),
            rating_methodology_applied=[
                schema.RatingMethodologyAppliedSchema(
                    rating_methodology_applied_name=_as_text(method)
                )
                for method in data.get("rating_methodologies_applied", [])
            ],
            industry_risks=[
                schema.IndustryRiskSchema(
                    industry_risk_name=_as_text(risk.get("industry_risk_name")),
                    industry_risk_score=_as_text(risk.get("industry_risk_score")),
                    industry_weight=float(risk.get("industry_weight")),
                )
                for risk in data.get("industry_risks", [])
            ],
            segmentation_criteria=schema.SegmentationCriteriaSchema(
                segmentation_criteria_name=_as_text(data.get("segmentation_criteria"))
            ),
            reporting_currency=schema.CurrencySchema(
                currency_code=_as_text(data.get("reporting_currency"))
            ),
            country_of_origin=schema.CountrySchema(
                country_name=_as_text(data.get("country_of_origin"))
            ),
            accounting_principles=_as_text(data.get("accounting_principles")),
            end_of_business_month=_as_text(data.get("end_of_business_month")),
            business_risk_profile=_as_text(data.get("business_risk_profile")),
            blended_industry_risk_profile=_as_text(
                data.get("blended_industry_risk_profile")
            ),
            competitive_positioning=_as_text(data.get("competitive_positioning")),
            market_share=_as_text(data.get("market_share")),
            diversification=_as_text(data.get("diversification")),
            operating_profitability=_as_text(data.get("operating_profitability")),
            sector_or_company_specific_factor_1=_as_text(
                data.get("sector_or_company_specific_factor_1")
            ),
            sector_or_company_specific_factor_2=(
                None
                if _is_missing(data.get("sector_or_company_specific_factor_2"))
                else _as_text(data.get("sector_or_company_specific_factor_2"))
            ),
            financial_risk_profile=_as_text(data.get("financial_risk_profile")),
            leverage=_as_text(data.get("leverage")),
            interest_cover=_as_text(data.get("interest_cover")),
            cash_flow_cover=_as_text(data.get("cash_flow_cover")),
            liquidity_assessment=_as_text(data.get("liquidity_assessment")),
            scope_credit_metrics=scope_credit_metrics,
        )

        industry_weights = [
            float(risk.get("industry_weight"))
            for risk in data.get("industry_risks", [])
            if not _is_missing(risk.get("industry_weight"))
        ]
        quality_report = _build_quality_report(
            raw_data=data,
            metric_statuses=metric_statuses,
            industry_weights=industry_weights,
        )

        return validated_data, quality_report
    except Exception as e:
        raise ValueError(f"Validation failed for {file_path}: {e}") from e
