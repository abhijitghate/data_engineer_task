from src.pipeline.validator import validate_data


def test_validate_data_returns_quality_report_with_warnings(tmp_path):
    file_path = tmp_path / "sample.xlsm"
    file_path.write_bytes(b"fake")

    raw_data = {
        "company_name": "Acme Corp",
        "corporate_sector": "Industrials",
        "rating_methodologies_applied": ["Method 1"],
        "industry_risks": [
            {
                "industry_risk_name": "Risk A",
                "industry_risk_score": "A",
                "industry_weight": 0.3,
            }
        ],
        "segmentation_criteria": "Segment 1",
        "reporting_currency": "EUR",
        "country_of_origin": "Germany",
        "accounting_principles": "",
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
                "scope_adjusted_ebitda_interest_cover": "bad-number",
                "scope_adjusted_debt_ebitda": "1.0",
                "scope_adjusted_ffo_debt": "2.0",
                "scope_adjusted_loan_value": "3.0",
                "scope_adjusted_focf_debt": "4.0",
                "liquidity": "5.0",
            }
        ],
    }

    _, report = validate_data(raw_data, "v1", str(file_path))

    assert report["completeness_rate"] < 1.0
    assert report["validity_rate"] < 1.0
    assert report["warning_count"] >= 1
    assert report["invalid_metric_values"] >= 1
