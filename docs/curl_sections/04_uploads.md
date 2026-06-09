# 4) Uploads

## Request 1

```bash
curl --location "http://localhost:8000/uploads"
```

### Response

```json
[
  {
    "upload_id": 4,
    "file_name": "corporates_B_2.xlsm",
    "storage_path": "data/corporates_B_2.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.799292Z",
    "upload_status": "success",
    "file_checksum": "57db65be38c7c21462eca69237baab153e7c29b5473f6334f6a890c084516441"
  },
  {
    "upload_id": 3,
    "file_name": "corporates_B_1.xlsm",
    "storage_path": "data/corporates_B_1.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.758334Z",
    "upload_status": "success",
    "file_checksum": "ef043cca3abaf3922ed34b3c247f58bea68c13160d514dfcf5c2b503997ffef6"
  },
  {
    "upload_id": 2,
    "file_name": "corporates_A_2.xlsm",
    "storage_path": "data/corporates_A_2.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.723872Z",
    "upload_status": "success",
    "file_checksum": "722818b3a18449ba49af14aa720df4311aceb33ae938e93183927d7f3454fa21"
  },
  {
    "upload_id": 1,
    "file_name": "corporates_A_1.xlsm",
    "storage_path": "data/corporates_A_1.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.669020Z",
    "upload_status": "success",
    "file_checksum": "04bf22f57e2b75c4701c429d2ab988ed1d2bf86f29b5944b3d87185c2c7ee09b"
  }
]
```

## Request 2

```bash
curl --location "http://localhost:8000/uploads/1/details"
```

### Response

```json
{
  "upload": {
    "upload_id": 1,
    "file_name": "corporates_A_1.xlsm",
    "storage_path": "data/corporates_A_1.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.669020Z",
    "upload_status": "success",
    "file_checksum": "04bf22f57e2b75c4701c429d2ab988ed1d2bf86f29b5944b3d87185c2c7ee09b"
  },
  "snapshots": [
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
}
```

## Request 3

```bash
curl --location "http://localhost:8000/uploads/stats"
```

### Response

```json
[
  {
    "upload_id": 4,
    "file_name": "corporates_B_2.xlsm",
    "storage_path": "data/corporates_B_2.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.799292Z",
    "upload_status": "success",
    "file_checksum": "57db65be38c7c21462eca69237baab153e7c29b5473f6334f6a890c084516441",
    "snapshot_count": 1,
    "company_count": 1,
    "metric_row_count": 10,
    "first_snapshot_at": "2026-06-09T19:17:50.799292Z",
    "last_snapshot_at": "2026-06-09T19:17:50.799292Z"
  },
  {
    "upload_id": 3,
    "file_name": "corporates_B_1.xlsm",
    "storage_path": "data/corporates_B_1.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.758334Z",
    "upload_status": "success",
    "file_checksum": "ef043cca3abaf3922ed34b3c247f58bea68c13160d514dfcf5c2b503997ffef6",
    "snapshot_count": 1,
    "company_count": 1,
    "metric_row_count": 10,
    "first_snapshot_at": "2026-06-09T19:17:50.758334Z",
    "last_snapshot_at": "2026-06-09T19:17:50.758334Z"
  },
  {
    "upload_id": 2,
    "file_name": "corporates_A_2.xlsm",
    "storage_path": "data/corporates_A_2.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.723872Z",
    "upload_status": "success",
    "file_checksum": "722818b3a18449ba49af14aa720df4311aceb33ae938e93183927d7f3454fa21",
    "snapshot_count": 1,
    "company_count": 1,
    "metric_row_count": 10,
    "first_snapshot_at": "2026-06-09T19:17:50.723872Z",
    "last_snapshot_at": "2026-06-09T19:17:50.723872Z"
  },
  {
    "upload_id": 1,
    "file_name": "corporates_A_1.xlsm",
    "storage_path": "data/corporates_A_1.xlsm",
    "discussion_version": "v1",
    "uploaded_at": "2026-06-09T19:17:50.669020Z",
    "upload_status": "success",
    "file_checksum": "04bf22f57e2b75c4701c429d2ab988ed1d2bf86f29b5944b3d87185c2c7ee09b",
    "snapshot_count": 1,
    "company_count": 1,
    "metric_row_count": 10,
    "first_snapshot_at": "2026-06-09T19:17:50.669020Z",
    "last_snapshot_at": "2026-06-09T19:17:50.669020Z"
  }
]
```

## Request 4

```bash
curl --location "http://localhost:8000/uploads/1/file"
```

### Response

```text
<no response captured in source file>
```
