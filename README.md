# Corporate Credit Rating Data Pipeline - Solution README

## 1. What This Project Delivers

This implementation builds a production-style data platform for corporate credit rating submissions stored in Excel `.xlsm` files.

It provides:
- Custom extraction from the `MASTER` sheet only.
- ETL orchestration with stages: Extract -> Validate -> Transform -> Load.
- Dimensional warehouse model with temporal tracking for companies and snapshots.
- Incremental + idempotent ingestion behavior.
- Data quality reporting and rule-level validation findings.
- Read-focused REST API for analytics and BI consumption.
- Containerized execution with Docker Compose.

## 2. Repository Layout

```text
src/
  application/
    routers/        # FastAPI route handlers
    services/       # business/service logic
    repositories/   # SQLAlchemy read queries against serving views/tables
    schemas/        # API response models
  pipeline/
    parser.py       # MASTER sheet extraction
    validator.py    # validation + quality findings
    transformer.py  # validated payload -> DB-ready payload
    loader.py       # transactional persistence + temporal updates
    pipeline.py     # orchestration, retry, run tracking, artifacts
  database/
    models.py       # SQLAlchemy ORM models
    schemas.py      # ingestion/validation Pydantic models

alembic/versions/   # schema + view migrations
reports/            # generated pipeline log + quality artifacts
docs/curl_sections/ # endpoint examples with sample responses
```

## 3. Architecture Overview

### 3.1 Data Flow

1. Parse input files from `data/*.xlsm` and read only `MASTER` sheet.
2. Validate payload fields, normalize values, and produce rule-level findings.
3. Transform validated object graph into DB-ready natural-key payloads.
4. Load transactionally into warehouse dimensions/facts/bridges.
5. Record pipeline run and per-file processing state.
6. Expose read models via FastAPI endpoints backed by serving views.

### 3.2 Runtime Components

Docker services:
- `postgres` -> warehouse storage
- `migrate` -> Alembic migration runner
- `api` -> FastAPI app on port `8000`
- `pipeline` -> ETL runner (CLI-driven)
- `test` -> DB-backed integration test profile

## 4. Key Design Decisions

### 4.1 Dimensional + Temporal Model

- `warehouse.dimension_companies` stores company versions (`company_version_id`) with:
  - `valid_from`, `valid_to`, `is_current`
- `warehouse.fact_company_snapshots` stores point-in-time submissions per upload.
- `warehouse.fact_scope_credit_metrics` stores time-series metric rows by `metric_year`.
- Bridge tables model many-to-many relationships for methodologies and industry risks.

Reasoning:
- Enables both "latest state" and "as-of" analytics.
- Supports re-submissions and historical comparison without destructive updates.

### 4.2 Idempotency + Incremental Loading

- SHA-256 file checksum computed per file.
- Short-circuit if checksum already ingested (idempotent behavior).
- `processed_files` table tracks per-run/per-file status and prevents redundant work.

Reasoning:
- Safe re-runs and reduced duplicate processing.

### 4.3 Serving Views for BI/API

Views in `applicationdatabase` provide stable read surfaces:
- `v_company_current_metadata`
- `v_company_versions`
- `v_company_snapshots_enriched`
- `v_company_metric_history`
- `v_upload_stats`

Reasoning:
- Keeps API/read concerns decoupled from raw warehouse joins.

### 4.4 Validation-as-Policy

Validation now emits structured findings with:
- `rule_id`
- `severity` (`error` or `warning`)
- `field`
- `message`

Error-level findings fail ingestion for that file.
Warning-level findings are retained for quality visibility.

## 5. Validation Framework Details

Validation is implemented in `src/pipeline/validator.py`.

### 5.1 Rule Coverage

Implemented checks include:
- Required fields present.
- Currency format validation (`[A-Z]{3}`).
- Business month normalization/validation.
- `metric_year` format/range validation (`1900`-`2100`).
- Duplicate detection:
  - rating methodologies
  - industry risk names
  - metric years
- Industry weight policy:
  - warning if near threshold mismatch
  - error if materially far from `1.0000`
- Metric status/value consistency:
  - `numeric` status requires non-null value
  - non-`numeric` status requires null value
- Suspicious value warnings for rating-scale fields outside known domain.

### 5.2 Quality Outputs

Per-file quality report includes:
- completeness rate
- validity rate
- warning count
- error count
- missing required fields
- invalid metric value count
- rule-level findings list

Run-level quality artifacts are saved as:
- `reports/quality_run_<run_id>.json`

### 5.3 Validation Lineage Persistence

Rule-level findings are persisted in:
- `warehouse.validation_findings`

This table stores run/file metadata with rule details for auditability and BI slicing.

## 6. API Endpoints

### 6.1 Health
- `GET /health`

### 6.2 Companies
- `GET /companies`
- `GET /companies/{company_id}`
- `GET /companies/{company_id}/versions`
- `GET /companies/{company_id}/history`
- `GET /companies/compare?company_ids=1&company_ids=2&as_of_date=YYYY-MM-DD`

### 6.3 Snapshots
- `GET /snapshots`
  - filters: `company_id`, `from_date`, `to_date`, `sector`, `country`, `currency`
- `GET /snapshots/{snapshot_id}`
- `GET /snapshots/latest`

### 6.4 Upload Audit
- `GET /uploads`
- `GET /uploads/{upload_id}/details`
- `GET /uploads/{upload_id}/file`
- `GET /uploads/stats`

### 6.5 Pipeline Observability
- `GET /pipeline/runs`
- `GET /pipeline/runs/{run_id}`
- `GET /pipeline/runs/{run_id}/quality`

For concrete request/response examples, see:
- `docs/curl_sections/*.md`

## 7. Setup and Run Commands

### 7.1 Prerequisites

- Docker + Docker Compose
- (Optional local run) Python 3.11+

### 7.2 Environment

**This step is crucial**
```bash
cp .env.example .env
# then edit .env secrets and connection strings
```

### 7.3 One-command Stack Startup

```bash
docker compose up
```
or detached mode 
```bash
docker compose up -d
```

This starts postgres, applies migrations, launches API, and can run pipeline via service command.

### 7.4 Run Ingestion Pipeline

Default bundled files:
```bash
docker compose run --rm pipeline
```

Custom version and retry settings:
```bash
docker compose run --rm \
  -e PIPELINE_ARGS="--version v2 --max-retries 5 --backoff-seconds 1.5" \
  pipeline
```

Custom file list:
```bash
docker compose run --rm \
  -e PIPELINE_ARGS="--files data/corporates_A_1.xlsm data/corporates_B_2.xlsm --version v3" \
  pipeline
```

### 7.5 API Access

Open Swagger UI:
- `http://localhost:8000/docs`

Quick health check:
```bash
curl --location "http://localhost:8000/health"
```

### 7.6 Run Tests

Inside compose (DB-backed integration tests):
```bash
docker compose --profile test run --rm test
```

Local unit/integration (non-DB):
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/unit
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/integration
```

Note: `tests/integration_db` expects the compose hostname/network (`postgres`).

## 8. Pipeline Outputs and Monitoring

Generated artifacts:
- Pipeline logs: `reports/pipeline_run_<run_id>.log`
- Quality artifact: `reports/quality_run_<run_id>.json`

Warehouse observability tables:
- `warehouse.pipeline_runs`
- `warehouse.processed_files`
- `warehouse.validation_findings`

These support end-to-end lineage from file -> pipeline run -> validation findings -> warehouse rows.

## 9. Migration Notes

Ensure latest schema is applied:

```bash
docker compose run --rm migrate
# or
alembic upgrade head
```

Latest migration includes validation findings persistence.

## 10. Known Constraints

- Input parser is purpose-built for this MASTER sheet layout; upstream template drift may require parser rule updates.
- DB-backed integration tests assume compose networking.
- API is intentionally read-only (no upload endpoint), consistent with assignment non-goals.

## 11. Deliverable Mapping

Implemented deliverables:
- Source repository with ETL + API + schema migrations.
- Docker Compose setup with orchestration and health checks.
- Sample outputs (`reports/*` and `docs/curl_sections/*`).
- Unit and integration tests.
- AI usage disclosure (`AI_USAGE.md`).


___
