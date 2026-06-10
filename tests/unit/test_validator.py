import pytest

from src.pipeline.validator import validate_data


def _valid_raw_data() -> dict:
    return {
        "company_name": "Acme Corp",
        "corporate_sector": "Industrials",
        "rating_methodologies_applied": ["Method 1", "Method 2"],
        "industry_risks": [
            {
                "industry_risk_name": "Risk A",
                "industry_risk_score": "BBB",
                "industry_weight": 0.6,
            },
            {
                "industry_risk_name": "Risk B",
                "industry_risk_score": "BB+",
                "industry_weight": 0.4,
            },
        ],
        "segmentation_criteria": "Segment 1",
        "reporting_currency": "EUR",
        "country_of_origin": "Germany",
        "accounting_principles": "IFRS",
        "end_of_business_month": "December",
        "business_risk_profile": "bbb",
        "blended_industry_risk_profile": "bbb",
        "competitive_positioning": "bbb",
        "market_share": "bbb",
        "diversification": "bbb",
        "operating_profitability": "bbb",
        "sector_or_company_specific_factor_1": "bbb",
        "sector_or_company_specific_factor_2": "bbb",
        "financial_risk_profile": "bbb",
        "leverage": "bbb",
        "interest_cover": "bbb",
        "cash_flow_cover": "bbb",
        "liquidity_assessment": "bbb",
        "scope_credit_metrics": [
            {
                "metric_year": "2024",
                "scope_adjusted_ebitda_interest_cover": "1.0",
                "scope_adjusted_debt_ebitda": "2.0",
                "scope_adjusted_ffo_debt": "3.0",
                "scope_adjusted_loan_value": "4.0",
                "scope_adjusted_focf_debt": "5.0",
                "liquidity": "6.0",
            },
            {
                "metric_year": "2025",
                "scope_adjusted_ebitda_interest_cover": "locked",
                "scope_adjusted_debt_ebitda": "locked",
                "scope_adjusted_ffo_debt": "locked",
                "scope_adjusted_loan_value": "locked",
                "scope_adjusted_focf_debt": "locked",
                "liquidity": "locked",
            },
        ],
    }


def test_validate_data_returns_structured_quality_report(tmp_path):
    file_path = tmp_path / "sample.xlsm"
    file_path.write_bytes(b"fake")
    raw_data = _valid_raw_data()

    _, report = validate_data(raw_data, "v1", str(file_path))

    assert report["completeness_rate"] == 1.0
    assert report["validity_rate"] == 1.0
    assert report["error_count"] == 0
    assert report["warning_count"] == 0
    assert report["findings"] == []


def test_validate_data_rejects_duplicate_metric_year(tmp_path):
    file_path = tmp_path / "sample.xlsm"
    file_path.write_bytes(b"fake")
    raw_data = _valid_raw_data()
    raw_data["scope_credit_metrics"][1]["metric_year"] = "2024"

    with pytest.raises(ValueError, match="Validation failed"):
        validate_data(raw_data, "v1", str(file_path))


def test_validate_data_rejects_invalid_currency_and_month(tmp_path):
    file_path = tmp_path / "sample.xlsm"
    file_path.write_bytes(b"fake")
    raw_data = _valid_raw_data()
    raw_data["reporting_currency"] = "Euro"
    raw_data["end_of_business_month"] = "Decembruary"

    with pytest.raises(ValueError, match="Validation failed"):
        validate_data(raw_data, "v1", str(file_path))


def test_validate_data_rejects_invalid_weight_sum_policy(tmp_path):
    file_path = tmp_path / "sample.xlsm"
    file_path.write_bytes(b"fake")
    raw_data = _valid_raw_data()
    raw_data["industry_risks"][0]["industry_weight"] = 0.8
    raw_data["industry_risks"][1]["industry_weight"] = 0.4

    with pytest.raises(ValueError, match="Validation failed"):
        validate_data(raw_data, "v1", str(file_path))
