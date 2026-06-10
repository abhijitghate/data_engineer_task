import hashlib
import math
import re
from typing import Any, TypedDict

import src.database.schemas as schema


class DataQualityFinding(TypedDict):
    rule_id: str
    severity: str
    field: str
    message: str


class DataQualityReport(TypedDict):
    completeness_rate: float
    validity_rate: float
    error_count: int
    warning_count: int
    missing_required_fields: list[str]
    invalid_metric_values: int
    total_metric_values: int
    warnings: list[str]
    findings: list[DataQualityFinding]


REQUIRED_FIELDS = [
    "company_name",
    "corporate_sector",
    "reporting_currency",
    "country_of_origin",
    "accounting_principles",
    "end_of_business_month",
    "segmentation_criteria",
]

WARN_WEIGHT_TOLERANCE = 0.001
ERROR_WEIGHT_TOLERANCE = 0.01

RATING_SCALE_VALUES = {
    "aaa",
    "aa+",
    "aa",
    "aa-",
    "a+",
    "a",
    "a-",
    "bbb+",
    "bbb",
    "bbb-",
    "bb+",
    "bb",
    "bb-",
    "b+",
    "b",
    "b-",
    "ccc",
    "cc",
    "c",
    "sd",
    "d",
}

RATING_LIKE_FIELDS = [
    "business_risk_profile",
    "blended_industry_risk_profile",
    "competitive_positioning",
    "market_share",
    "diversification",
    "operating_profitability",
    "sector_or_company_specific_factor_1",
    "sector_or_company_specific_factor_2",
    "financial_risk_profile",
    "leverage",
    "interest_cover",
    "cash_flow_cover",
    "liquidity_assessment",
]

ISO_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
YEAR_PATTERN = re.compile(r"^\d{4}$")

MONTH_LOOKUP = {
    "1": "January",
    "01": "January",
    "jan": "January",
    "january": "January",
    "2": "February",
    "02": "February",
    "feb": "February",
    "february": "February",
    "3": "March",
    "03": "March",
    "mar": "March",
    "march": "March",
    "4": "April",
    "04": "April",
    "apr": "April",
    "april": "April",
    "5": "May",
    "05": "May",
    "may": "May",
    "6": "June",
    "06": "June",
    "jun": "June",
    "june": "June",
    "7": "July",
    "07": "July",
    "jul": "July",
    "july": "July",
    "8": "August",
    "08": "August",
    "aug": "August",
    "august": "August",
    "9": "September",
    "09": "September",
    "sep": "September",
    "sept": "September",
    "september": "September",
    "10": "October",
    "oct": "October",
    "october": "October",
    "11": "November",
    "nov": "November",
    "november": "November",
    "12": "December",
    "dec": "December",
    "december": "December",
}


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


def _build_finding(
    rule_id: str,
    severity: str,
    field: str,
    message: str,
) -> DataQualityFinding:
    return DataQualityFinding(
        rule_id=rule_id,
        severity=severity,
        field=field,
        message=message,
    )


def _normalize_month(raw_value: Any) -> str | None:
    key = _as_text(raw_value).lower()
    if key in MONTH_LOOKUP:
        return MONTH_LOOKUP[key]
    return None


def _is_rating_scale_value(value: str) -> bool:
    return value.lower() in RATING_SCALE_VALUES


def _validate_metric_year(metric_year: str) -> bool:
    if not YEAR_PATTERN.match(metric_year):
        return False
    parsed = int(metric_year)
    return 1900 <= parsed <= 2100


def _validate_metric_status_consistency(
    metric: schema.ScopeCreditMetricSchema,
    row_index: int,
) -> list[DataQualityFinding]:
    findings: list[DataQualityFinding] = []
    checks = [
        (
            "scope_adjusted_ebitda_interest_cover",
            metric.scope_adjusted_ebitda_interest_cover,
            metric.scope_adjusted_ebitda_interest_cover_status,
        ),
        (
            "scope_adjusted_debt_ebitda",
            metric.scope_adjusted_debt_ebitda,
            metric.scope_adjusted_debt_ebitda_status,
        ),
        (
            "scope_adjusted_ffo_debt",
            metric.scope_adjusted_ffo_debt,
            metric.scope_adjusted_ffo_debt_status,
        ),
        (
            "scope_adjusted_loan_value",
            metric.scope_adjusted_loan_value,
            metric.scope_adjusted_loan_value_status,
        ),
        (
            "scope_adjusted_focf_debt",
            metric.scope_adjusted_focf_debt,
            metric.scope_adjusted_focf_debt_status,
        ),
        ("liquidity", metric.liquidity, metric.liquidity_status),
    ]
    for field_name, value, status in checks:
        if status == "numeric" and value is None:
            findings.append(
                _build_finding(
                    rule_id="METRIC_STATUS_VALUE_MISMATCH",
                    severity="error",
                    field=f"scope_credit_metrics[{row_index}].{field_name}",
                    message="Status is numeric but value is null.",
                )
            )
        if status != "numeric" and value is not None:
            findings.append(
                _build_finding(
                    rule_id="METRIC_STATUS_VALUE_MISMATCH",
                    severity="error",
                    field=f"scope_credit_metrics[{row_index}].{field_name}",
                    message=f"Status is {status} but value is present.",
                )
            )
    return findings


def _build_quality_report(
    raw_data: dict,
    metric_statuses: list[schema.MetricStatus],
    findings: list[DataQualityFinding],
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

    warnings: list[str] = [
        item["message"] for item in findings if item["severity"] == "warning"
    ]
    errors = [item for item in findings if item["severity"] == "error"]

    return DataQualityReport(
        completeness_rate=round(completeness_rate, 4),
        validity_rate=round(validity_rate, 4),
        error_count=len(errors),
        warning_count=len([item for item in findings if item["severity"] == "warning"]),
        missing_required_fields=missing_required_fields,
        invalid_metric_values=invalid_metric_values,
        total_metric_values=total_metric_values,
        warnings=warnings,
        findings=findings,
    )


def validate_data(
    data: dict, version: str, file_path: str
) -> tuple[schema.IngestionSchema, DataQualityReport]:
    try:
        file_name = file_path.split("/")[-1]
        file_checksum = _compute_sha256(file_path)

        findings: list[DataQualityFinding] = []

        for field_name in REQUIRED_FIELDS:
            if _is_missing(data.get(field_name)):
                findings.append(
                    _build_finding(
                        rule_id="REQUIRED_FIELD_MISSING",
                        severity="error",
                        field=field_name,
                        message=f"Required field '{field_name}' is missing.",
                    )
                )

        normalized_month = _normalize_month(data.get("end_of_business_month"))
        if normalized_month is None:
            findings.append(
                _build_finding(
                    rule_id="INVALID_BUSINESS_MONTH",
                    severity="error",
                    field="end_of_business_month",
                    message="End of business month must be a valid month value.",
                )
            )
            normalized_month = _as_text(data.get("end_of_business_month"))

        currency_code = _as_text(data.get("reporting_currency")).upper()
        if currency_code and not ISO_CURRENCY_PATTERN.match(currency_code):
            findings.append(
                _build_finding(
                    rule_id="INVALID_CURRENCY_CODE",
                    severity="error",
                    field="reporting_currency",
                    message="Reporting currency must be a 3-letter uppercase code.",
                )
            )

        methodologies: list[schema.RatingMethodologyAppliedSchema] = []
        seen_methods: set[str] = set()
        for index, method in enumerate(data.get("rating_methodologies_applied", [])):
            cleaned_method = _as_text(method)
            if _is_missing(cleaned_method):
                findings.append(
                    _build_finding(
                        rule_id="EMPTY_RATING_METHODOLOGY",
                        severity="error",
                        field=f"rating_methodologies_applied[{index}]",
                        message="Rating methodology cannot be empty.",
                    )
                )
                continue
            dedupe_key = cleaned_method.lower()
            if dedupe_key in seen_methods:
                findings.append(
                    _build_finding(
                        rule_id="DUPLICATE_RATING_METHODOLOGY",
                        severity="error",
                        field=f"rating_methodologies_applied[{index}]",
                        message=f"Duplicate rating methodology '{cleaned_method}'.",
                    )
                )
                continue
            seen_methods.add(dedupe_key)
            methodologies.append(
                schema.RatingMethodologyAppliedSchema(
                    rating_methodology_applied_name=cleaned_method
                )
            )

        industry_risks: list[schema.IndustryRiskSchema] = []
        seen_industry_risks: set[str] = set()
        for index, risk in enumerate(data.get("industry_risks", [])):
            risk_name = _as_text(risk.get("industry_risk_name"))
            if _is_missing(risk_name):
                findings.append(
                    _build_finding(
                        rule_id="EMPTY_INDUSTRY_RISK_NAME",
                        severity="error",
                        field=f"industry_risks[{index}].industry_risk_name",
                        message="Industry risk name cannot be empty.",
                    )
                )
                continue
            risk_key = risk_name.lower()
            if risk_key in seen_industry_risks:
                findings.append(
                    _build_finding(
                        rule_id="DUPLICATE_INDUSTRY_RISK_NAME",
                        severity="error",
                        field=f"industry_risks[{index}].industry_risk_name",
                        message=f"Duplicate industry risk '{risk_name}'.",
                    )
                )
                continue
            seen_industry_risks.add(risk_key)

            risk_score = _as_text(risk.get("industry_risk_score"))
            if risk_score and not _is_rating_scale_value(risk_score):
                findings.append(
                    _build_finding(
                        rule_id="SUSPICIOUS_INDUSTRY_RISK_SCORE",
                        severity="warning",
                        field=f"industry_risks[{index}].industry_risk_score",
                        message=f"Industry risk score '{risk_score}' is outside known rating scale values.",
                    )
                )
            try:
                risk_weight = float(risk.get("industry_weight"))
            except (TypeError, ValueError):
                findings.append(
                    _build_finding(
                        rule_id="INVALID_INDUSTRY_WEIGHT",
                        severity="error",
                        field=f"industry_risks[{index}].industry_weight",
                        message="Industry weight must be numeric.",
                    )
                )
                continue
            if risk_weight < 0 or risk_weight > 1:
                findings.append(
                    _build_finding(
                        rule_id="INVALID_INDUSTRY_WEIGHT_RANGE",
                        severity="error",
                        field=f"industry_risks[{index}].industry_weight",
                        message="Industry weight must be between 0 and 1.",
                    )
                )
                continue
            industry_risks.append(
                schema.IndustryRiskSchema(
                    industry_risk_name=risk_name,
                    industry_risk_score=risk_score,
                    industry_weight=risk_weight,
                )
            )

        scope_credit_metrics = []
        metric_statuses: list[schema.MetricStatus] = []
        seen_metric_years: set[str] = set()
        for metric in data.get("scope_credit_metrics", []):
            metric_year = _as_text(metric.get("metric_year"))
            metric_row = len(scope_credit_metrics)
            if not _validate_metric_year(metric_year):
                findings.append(
                    _build_finding(
                        rule_id="INVALID_METRIC_YEAR",
                        severity="error",
                        field=f"scope_credit_metrics[{metric_row}].metric_year",
                        message=f"Metric year '{metric_year}' must be a 4-digit year between 1900 and 2100.",
                    )
                )
            elif metric_year in seen_metric_years:
                findings.append(
                    _build_finding(
                        rule_id="DUPLICATE_METRIC_YEAR",
                        severity="error",
                        field=f"scope_credit_metrics[{metric_row}].metric_year",
                        message=f"Duplicate metric year '{metric_year}' in payload.",
                    )
                )
            else:
                seen_metric_years.add(metric_year)

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

            metric_row_schema = schema.ScopeCreditMetricSchema(
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
                metric_year=metric_year,
            )
            findings.extend(
                _validate_metric_status_consistency(metric_row_schema, metric_row)
            )
            scope_credit_metrics.append(metric_row_schema)

        industry_weights = [risk.industry_weight for risk in industry_risks]
        if industry_weights:
            total_weight = sum(industry_weights)
            diff = abs(total_weight - 1.0)
            if diff > ERROR_WEIGHT_TOLERANCE:
                findings.append(
                    _build_finding(
                        rule_id="INDUSTRY_WEIGHT_SUM_OUT_OF_RANGE",
                        severity="error",
                        field="industry_risks.industry_weight",
                        message=f"Industry weights sum is {total_weight:.4f} (expected 1.0000).",
                    )
                )
            elif diff > WARN_WEIGHT_TOLERANCE:
                findings.append(
                    _build_finding(
                        rule_id="INDUSTRY_WEIGHT_SUM_NEAR_THRESHOLD",
                        severity="warning",
                        field="industry_risks.industry_weight",
                        message=f"Industry weights sum is {total_weight:.4f} (expected 1.0000).",
                    )
                )

        for field_name in RATING_LIKE_FIELDS:
            value = _as_text(data.get(field_name))
            if value and not _is_rating_scale_value(value):
                findings.append(
                    _build_finding(
                        rule_id="SUSPICIOUS_RATING_VALUE",
                        severity="warning",
                        field=field_name,
                        message=f"Value '{value}' is outside known rating scale values.",
                    )
                )

        validated_data = schema.IngestionSchema(
            file_name=file_name,
            storage_path=file_path,
            discussion_version=version,
            file_checksum=file_checksum,
            company_name=_as_text(data.get("company_name")),
            sector=schema.SectorSchema(sector_name=_as_text(data.get("corporate_sector"))),
            rating_methodology_applied=methodologies,
            industry_risks=industry_risks,
            segmentation_criteria=schema.SegmentationCriteriaSchema(
                segmentation_criteria_name=_as_text(data.get("segmentation_criteria"))
            ),
            reporting_currency=schema.CurrencySchema(
                currency_code=currency_code
            ),
            country_of_origin=schema.CountrySchema(
                country_name=_as_text(data.get("country_of_origin"))
            ),
            accounting_principles=_as_text(data.get("accounting_principles")),
            end_of_business_month=normalized_month,
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

        quality_report = _build_quality_report(
            raw_data=data,
            metric_statuses=metric_statuses,
            findings=findings,
        )

        if quality_report["error_count"] > 0:
            raise ValueError(
                f"Validation failed with {quality_report['error_count']} error(s)."
            )

        return validated_data, quality_report
    except Exception as e:
        raise ValueError(f"Validation failed for {file_path}: {e}") from e
