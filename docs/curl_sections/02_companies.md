# 2) Companies

## Request 1

```bash
curl --location "http://localhost:8000/companies"
```

### Response

```json
[
  {
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "sector_name": "Personal & Household Goods",
    "country_name": "Federal Republic of Germany",
    "currency_code": "EUR",
    "accounting_principles": "IFRS",
    "end_of_business_month": "December",
    "company_valid_from": "2026-06-09T19:17:50.669020Z",
    "company_valid_to": "9999-12-31T23:59:59.999999Z",
    "is_current_company_version": true
  },
  {
    "company_id": 2,
    "company_version_id": 2,
    "company_name": "Company B",
    "sector_name": "Automobiles & Parts",
    "country_name": "Swiss Confederation",
    "currency_code": "CHF",
    "accounting_principles": "IFRS",
    "end_of_business_month": "March",
    "company_valid_from": "2026-06-09T19:17:50.758334Z",
    "company_valid_to": "9999-12-31T23:59:59.999999Z",
    "is_current_company_version": true
  }
]
```

## Request 2

```bash
curl --location "http://localhost:8000/companies/1"
```

### Response

```json
{
  "snapshot_id": 2,
  "upload_id": 2,
  "discussion_version": "v1",
  "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
  "snapshot_status": "success",
  "company_id": 1,
  "company_version_id": 1,
  "company_name": "Company A",
  "sector_name": "Personal & Household Goods",
  "country_name": "Federal Republic of Germany",
  "currency_code": "EUR",
  "segmentation_criteria_name": "EBITDA contribution",
  "business_risk_profile": "B",
  "blended_industry_risk_profile": "A",
  "competitive_positioning": "B+",
  "market_share": "B+",
  "diversification": "B+",
  "operating_profitability": "B",
  "financial_risk_profile": "CC",
  "leverage": "CCC",
  "interest_cover": "B-",
  "cash_flow_cover": "CCC",
  "liquidity_assessment": "4.862"
}
```

## Request 3

```bash
curl --location "http://localhost:8000/companies/1/versions"
```

### Response

```json
[
  {
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "sector_name": "Personal & Household Goods",
    "country_name": "Federal Republic of Germany",
    "currency_code": "EUR",
    "accounting_principles": "IFRS",
    "end_of_business_month": "December",
    "company_valid_from": "2026-06-09T19:17:50.669020Z",
    "company_valid_to": "9999-12-31T23:59:59.999999Z",
    "is_current_company_version": true,
    "first_snapshot_at": "2026-06-09T19:17:50.669020Z",
    "last_snapshot_at": "2026-06-09T19:17:50.723872Z",
    "snapshot_count": 2
  }
]
```

## Request 4

```bash
curl --location "http://localhost:8000/companies/1/history"
```

### Response

```json
[
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2027E",
    "scope_adjusted_ebitda_interest_cover": 18.4913,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 8.0,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 4.862,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 23.0,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2026E",
    "scope_adjusted_ebitda_interest_cover": 18.4913,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 29.0,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2025E",
    "scope_adjusted_ebitda_interest_cover": 36.8,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 36.8,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 29.0,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2024.0",
    "scope_adjusted_ebitda_interest_cover": 36.8,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 36.8,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 29.0,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2023",
    "scope_adjusted_ebitda_interest_cover": 4.862,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 27.329,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": null,
    "scope_adjusted_loan_value_status": "no_data",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2022.0",
    "scope_adjusted_ebitda_interest_cover": 4.862,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 36.8,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 36.8,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2021.0",
    "scope_adjusted_ebitda_interest_cover": 4.862,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 36.8,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 36.8,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 21.5319,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2020.0",
    "scope_adjusted_ebitda_interest_cover": 27.329,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 22.0,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 21.5319,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 4.862,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2019.0",
    "scope_adjusted_ebitda_interest_cover": 27.329,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 22.0,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 21.5319,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 4.862,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 2,
    "upload_id": 2,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "metric_year": "2018",
    "scope_adjusted_ebitda_interest_cover": 27.329,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 22.0,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 21.5319,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 4.862,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2027E",
    "scope_adjusted_ebitda_interest_cover": 18.4913,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 4.862,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 4.862,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2026E",
    "scope_adjusted_ebitda_interest_cover": 18.4913,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 27.329,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2025E",
    "scope_adjusted_ebitda_interest_cover": 36.8,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 36.8,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 27.329,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2024.0",
    "scope_adjusted_ebitda_interest_cover": 36.8,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 36.8,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 27.329,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2023",
    "scope_adjusted_ebitda_interest_cover": 4.862,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 27.329,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": null,
    "scope_adjusted_loan_value_status": "no_data",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2022.0",
    "scope_adjusted_ebitda_interest_cover": 4.862,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 36.8,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 36.8,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 4.862,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2021.0",
    "scope_adjusted_ebitda_interest_cover": 4.862,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 36.8,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 36.8,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 21.5319,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 21.5319,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2020.0",
    "scope_adjusted_ebitda_interest_cover": 27.329,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 27.329,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 21.5319,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 4.862,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2019",
    "scope_adjusted_ebitda_interest_cover": 27.329,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 27.329,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 21.5319,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 4.862,
    "liquidity_status": "numeric"
  },
  {
    "snapshot_id": 1,
    "upload_id": 1,
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "discussion_version": "v1",
    "snapshot_ingested_at": "2026-06-09T19:17:50.669020Z",
    "metric_year": "2018",
    "scope_adjusted_ebitda_interest_cover": 27.329,
    "scope_adjusted_ebitda_interest_cover_status": "numeric",
    "scope_adjusted_debt_ebitda": 18.4913,
    "scope_adjusted_debt_ebitda_status": "numeric",
    "scope_adjusted_ffo_debt": 27.329,
    "scope_adjusted_ffo_debt_status": "numeric",
    "scope_adjusted_loan_value": 27.329,
    "scope_adjusted_loan_value_status": "numeric",
    "scope_adjusted_focf_debt": 21.5319,
    "scope_adjusted_focf_debt_status": "numeric",
    "liquidity": 4.862,
    "liquidity_status": "numeric"
  }
]
```

## Request 5

```bash
curl --location "http://localhost:8000/companies/compare?company_ids=1&company_ids=1&as_of_date=2026-06-09"
```

### Response

```json
[
  {
    "company_id": 1,
    "company_version_id": 1,
    "company_name": "Company A",
    "sector_name": "Personal & Household Goods",
    "country_name": "Federal Republic of Germany",
    "currency_code": "EUR",
    "as_of_snapshot_id": 2,
    "as_of_snapshot_ingested_at": "2026-06-09T19:17:50.723872Z",
    "discussion_version": "v1"
  }
]
```
