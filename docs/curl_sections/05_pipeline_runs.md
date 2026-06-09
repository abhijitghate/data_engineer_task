# 5) Pipeline runs

## Request 1

```bash
curl --location "http://localhost:8000/pipeline/runs"
```

### Response

```json
[
  {
    "run_id": 1,
    "discussion_version": "v1",
    "started_at": "2026-06-09T19:17:50.601027Z",
    "finished_at": "2026-06-09T19:17:50.812587Z",
    "status": "success",
    "files_total": 4,
    "files_processed": 4,
    "files_succeeded": 4,
    "files_failed": 0,
    "files_skipped": 0,
    "quality_completeness_avg": 1.0,
    "quality_validity_avg": 1.0,
    "quality_warning_count": 0,
    "extract_ms_total": 113,
    "validate_ms_total": 0,
    "transform_ms_total": 0,
    "load_ms_total": 66,
    "duration_ms": 228,
    "error_summary": null
  }
]
```

## Request 2

```bash
curl --location "http://localhost:8000/pipeline/runs/1"
```

### Response

```json
{
  "run_id": 1,
  "discussion_version": "v1",
  "started_at": "2026-06-09T19:17:50.601027Z",
  "finished_at": "2026-06-09T19:17:50.812587Z",
  "status": "success",
  "files_total": 4,
  "files_processed": 4,
  "files_succeeded": 4,
  "files_failed": 0,
  "files_skipped": 0,
  "quality_completeness_avg": 1.0,
  "quality_validity_avg": 1.0,
  "quality_warning_count": 0,
  "extract_ms_total": 113,
  "validate_ms_total": 0,
  "transform_ms_total": 0,
  "load_ms_total": 66,
  "duration_ms": 228,
  "error_summary": null
}
```

## Request 3

```bash
curl --location "http://localhost:8000/pipeline/runs/1/quality"
```

### Response

```json
{
  "run": {
    "run_id": 1,
    "discussion_version": "v1",
    "started_at": "2026-06-09T19:17:50.601027Z",
    "finished_at": "2026-06-09T19:17:50.812587Z",
    "status": "success",
    "files_total": 4,
    "files_processed": 4,
    "files_succeeded": 4,
    "files_failed": 0,
    "files_skipped": 0,
    "quality_completeness_avg": 1.0,
    "quality_validity_avg": 1.0,
    "quality_warning_count": 0,
    "extract_ms_total": 113,
    "validate_ms_total": 0,
    "transform_ms_total": 0,
    "load_ms_total": 66,
    "duration_ms": 228,
    "error_summary": null
  },
  "files": [
    {
      "processed_file_id": 4,
      "run_id": 1,
      "file_name": "corporates_B_2.xlsm",
      "file_path": "data/corporates_B_2.xlsm",
      "file_checksum": "57db65be38c7c21462eca69237baab153e7c29b5473f6334f6a890c084516441",
      "discussion_version": "v1",
      "status": "success",
      "upload_id": 4,
      "company_id": 2,
      "company_version_id": 2,
      "snapshot_id": 4,
      "quality_completeness_rate": 1.0,
      "quality_validity_rate": 1.0,
      "quality_warning_count": 0,
      "quality_warnings": "",
      "extract_ms": 20,
      "validate_ms": 0,
      "transform_ms": 0,
      "load_ms": 10,
      "total_ms": 30,
      "error_message": null,
      "processed_at": "2026-06-09T19:17:50.809312Z"
    },
    {
      "processed_file_id": 3,
      "run_id": 1,
      "file_name": "corporates_B_1.xlsm",
      "file_path": "data/corporates_B_1.xlsm",
      "file_checksum": "ef043cca3abaf3922ed34b3c247f58bea68c13160d514dfcf5c2b503997ffef6",
      "discussion_version": "v1",
      "status": "success",
      "upload_id": 3,
      "company_id": 2,
      "company_version_id": 2,
      "snapshot_id": 3,
      "quality_completeness_rate": 1.0,
      "quality_validity_rate": 1.0,
      "quality_warning_count": 0,
      "quality_warnings": "",
      "extract_ms": 18,
      "validate_ms": 0,
      "transform_ms": 0,
      "load_ms": 15,
      "total_ms": 34,
      "error_message": null,
      "processed_at": "2026-06-09T19:17:50.773523Z"
    },
    {
      "processed_file_id": 2,
      "run_id": 1,
      "file_name": "corporates_A_2.xlsm",
      "file_path": "data/corporates_A_2.xlsm",
      "file_checksum": "722818b3a18449ba49af14aa720df4311aceb33ae938e93183927d7f3454fa21",
      "discussion_version": "v1",
      "status": "success",
      "upload_id": 2,
      "company_id": 1,
      "company_version_id": 1,
      "snapshot_id": 2,
      "quality_completeness_rate": 1.0,
      "quality_validity_rate": 1.0,
      "quality_warning_count": 0,
      "quality_warnings": "",
      "extract_ms": 17,
      "validate_ms": 0,
      "transform_ms": 0,
      "load_ms": 11,
      "total_ms": 29,
      "error_message": null,
      "processed_at": "2026-06-09T19:17:50.734827Z"
    },
    {
      "processed_file_id": 1,
      "run_id": 1,
      "file_name": "corporates_A_1.xlsm",
      "file_path": "data/corporates_A_1.xlsm",
      "file_checksum": "04bf22f57e2b75c4701c429d2ab988ed1d2bf86f29b5944b3d87185c2c7ee09b",
      "discussion_version": "v1",
      "status": "success",
      "upload_id": 1,
      "company_id": 1,
      "company_version_id": 1,
      "snapshot_id": 1,
      "quality_completeness_rate": 1.0,
      "quality_validity_rate": 1.0,
      "quality_warning_count": 0,
      "quality_warnings": "",
      "extract_ms": 58,
      "validate_ms": 0,
      "transform_ms": 0,
      "load_ms": 30,
      "total_ms": 90,
      "error_message": null,
      "processed_at": "2026-06-09T19:17:50.699376Z"
    }
  ],
  "artifact": {
    "run_id": 1,
    "discussion_version": "v1",
    "summary": {
      "files_total": 4,
      "files_processed": 4,
      "files_succeeded": 4,
      "files_failed": 0,
      "files_skipped": 0,
      "quality_completeness_avg": 1.0,
      "quality_validity_avg": 1.0,
      "quality_warning_count": 0,
      "duration_ms": 228
    },
    "files": [
      {
        "file_path": "data/corporates_A_1.xlsm",
        "status": "success",
        "quality_report": {
          "completeness_rate": 1.0,
          "validity_rate": 1.0,
          "warning_count": 0,
          "missing_required_fields": [],
          "invalid_metric_values": 0,
          "total_metric_values": 60,
          "warnings": []
        },
        "timings": {
          "extract_ms": 58,
          "validate_ms": 0,
          "transform_ms": 0,
          "load_ms": 30,
          "total_ms": 90
        }
      },
      {
        "file_path": "data/corporates_A_2.xlsm",
        "status": "success",
        "quality_report": {
          "completeness_rate": 1.0,
          "validity_rate": 1.0,
          "warning_count": 0,
          "missing_required_fields": [],
          "invalid_metric_values": 0,
          "total_metric_values": 60,
          "warnings": []
        },
        "timings": {
          "extract_ms": 17,
          "validate_ms": 0,
          "transform_ms": 0,
          "load_ms": 11,
          "total_ms": 29
        }
      },
      {
        "file_path": "data/corporates_B_1.xlsm",
        "status": "success",
        "quality_report": {
          "completeness_rate": 1.0,
          "validity_rate": 1.0,
          "warning_count": 0,
          "missing_required_fields": [],
          "invalid_metric_values": 0,
          "total_metric_values": 60,
          "warnings": []
        },
        "timings": {
          "extract_ms": 18,
          "validate_ms": 0,
          "transform_ms": 0,
          "load_ms": 15,
          "total_ms": 34
        }
      },
      {
        "file_path": "data/corporates_B_2.xlsm",
        "status": "success",
        "quality_report": {
          "completeness_rate": 1.0,
          "validity_rate": 1.0,
          "warning_count": 0,
          "missing_required_fields": [],
          "invalid_metric_values": 0,
          "total_metric_values": 60,
          "warnings": []
        },
        "timings": {
          "extract_ms": 20,
          "validate_ms": 0,
          "transform_ms": 0,
          "load_ms": 10,
          "total_ms": 30
        }
      }
    ]
  }
}
```
