# 3) Snapshots

## Request 1

```bash
curl --location "http://localhost:8000/snapshots?company_id=1&from_date=2026-06-09&to_date=2026-06-09&sector=Personal%20%26%20Household%20Goods&country=Federal%20Republic%20of%20Germany&currency=EUR"
```

### Response

```json
[
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "file_name": "corporates_A_2.xlsm",
    "storage_path": "data/corporates_A_2.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.723872Z",
    "upload_status": "success",
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "sector_name": "Personal & Household Goods",
    "country_name": "Federal Republic of Germany",
    "currency_code": "EUR",
    "accounting_principles": "IFRS",
    "end_of_business_month": "December",
    "segmentation_criteria_name": "EBITDA contribution",
    "business_risk_profile": "B",
    "blended_industry_risk_profile": "A",
    "competitive_positioning": "B+",
    "market_share": "B+",
    "diversification": "B+",
    "operating_profitability": "B",
    "sector_or_company_specific_factor_1": "B-",
    "sector_or_company_specific_factor_2": null,
    "financial_risk_profile": "CC",
    "leverage": "CCC",
    "interest_cover": "B-",
    "cash_flow_cover": "CCC",
    "liquidity_assessment": "4.862",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "snapshot_valid_from": "2026-06-09T19:17:50.723872Z",
    "snapshot_valid_to": "9999-12-31T23:59:59.999999Z",
    "snapshot_status": "success"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "file_name": "corporates_A_1.xlsm",
    "storage_path": "data/corporates_A_1.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.669020Z",
    "upload_status": "success",
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "sector_name": "Personal & Household Goods",
    "country_name": "Federal Republic of Germany",
    "currency_code": "EUR",
    "accounting_principles": "IFRS",
    "end_of_business_month": "December",
    "segmentation_criteria_name": "EBITDA contribution",
    "business_risk_profile": "B+",
    "blended_industry_risk_profile": "A",
    "competitive_positioning": "B+",
    "market_share": "BB-",
    "diversification": "B+",
    "operating_profitability": "BB-",
    "sector_or_company_specific_factor_1": "B-",
    "sector_or_company_specific_factor_2": null,
    "financial_risk_profile": "C",
    "leverage": "CCC",
    "interest_cover": "B-",
    "cash_flow_cover": "CCC",
    "liquidity_assessment": "4.862",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "snapshot_valid_from": "2026-06-09T19:17:50.669020Z",
    "snapshot_valid_to": "2026-06-09T19:17:50.729098Z",
    "snapshot_status": "success"
  }
]
```

## Request 2

```bash
curl --location "http://localhost:8000/snapshots/1"
```

### Response

```json
{
  "snapshot_id": 1,
  "upload_id": 1,
  "file_name": "corporates_A_1.xlsm",
  "storage_path": "data/corporates_A_1.xlsm",
  "discussion_version": "v1",
  "uploaded_at": "2026-06-09T19:17:50.669020Z",
  "upload_status": "success",
  "company_id": 1,
  "company_version_id": 1,
  "company_name": "Company A",
  "sector_name": "Personal & Household Goods",
  "country_name": "Federal Republic of Germany",
  "currency_code": "EUR",
  "accounting_principles": "IFRS",
  "end_of_business_month": "December",
  "segmentation_criteria_name": "EBITDA contribution",
  "business_risk_profile": "B+",
  "blended_industry_risk_profile": "A",
  "competitive_positioning": "B+",
  "market_share": "BB-",
  "diversification": "B+",
  "operating_profitability": "BB-",
  "sector_or_company_specific_factor_1": "B-",
  "sector_or_company_specific_factor_2": null,
  "financial_risk_profile": "C",
  "leverage": "CCC",
  "interest_cover": "B-",
  "cash_flow_cover": "CCC",
  "liquidity_assessment": "4.862",
  "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
  "snapshot_valid_from": "2026-06-09T19:17:50.669020Z",
  "snapshot_valid_to": "2026-06-09T19:17:50.729098Z",
  "snapshot_status": "success"
}
```

## Request 3

```bash
curl --location "http://localhost:8000/snapshots/latest"
```

### Response

```json
[
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "file_name": "corporates_A_2.xlsm",
    "storage_path": "data/corporates_A_2.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.723872Z",
    "upload_status": "success",
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "sector_name": "Personal & Household Goods",
    "country_name": "Federal Republic of Germany",
    "currency_code": "EUR",
    "accounting_principles": "IFRS",
    "end_of_business_month": "December",
    "segmentation_criteria_name": "EBITDA contribution",
    "business_risk_profile": "B",
    "blended_industry_risk_profile": "A",
    "competitive_positioning": "B+",
    "market_share": "B+",
    "diversification": "B+",
    "operating_profitability": "B",
    "sector_or_company_specific_factor_1": "B-",
    "sector_or_company_specific_factor_2": null,
    "financial_risk_profile": "CC",
    "leverage": "CCC",
    "interest_cover": "B-",
    "cash_flow_cover": "CCC",
    "liquidity_assessment": "4.862",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "snapshot_valid_from": "2026-06-09T19:17:50.723872Z",
    "snapshot_valid_to": "9999-12-31T23:59:59.999999Z",
    "snapshot_status": "success"
  },
  {
    "snapshot_id": 4,
    "upload_id": 4,
    "file_name": "corporates_B_2.xlsm",
    "storage_path": "data/corporates_B_2.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.799292Z",
    "upload_status": "success",
    "company_id": 2,
    "company_version_id": 2,
    "company_name": "Company B",
    "sector_name": "Automobiles & Parts",
    "country_name": "Swiss Confederation",
    "currency_code": "CHF",
    "accounting_principles": "IFRS",
    "end_of_business_month": "March",
    "segmentation_criteria_name": "EBITDA contribution",
    "business_risk_profile": "BBB-",
    "blended_industry_risk_profile": "A",
    "competitive_positioning": "A+",
    "market_share": "BBB+",
    "diversification": "A-",
    "operating_profitability": "BB+",
    "sector_or_company_specific_factor_1": "BBB+",
    "sector_or_company_specific_factor_2": null,
    "financial_risk_profile": "BB",
    "leverage": "BB+",
    "interest_cover": "BBB+",
    "cash_flow_cover": "A-",
    "liquidity_assessment": "1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.799292Z",
    "snapshot_valid_from": "2026-06-09T19:17:50.799292Z",
    "snapshot_valid_to": "9999-12-31T23:59:59.999999Z",
    "snapshot_status": "success"
  }
]
```
