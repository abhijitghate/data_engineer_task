CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS applicationdatabase;

-- Upload/audit trail (lineage + idempotency)
CREATE TABLE warehouse.upload_logs (
    upload_id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    discussion_version VARCHAR(50) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    upload_status VARCHAR(50) DEFAULT 'success' NOT NULL,
    file_checksum VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE warehouse.dimension_sectors (
    sector_id SERIAL PRIMARY KEY,
    sector_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE warehouse.dimension_countries (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE warehouse.dimension_currencies (
    currency_id SERIAL PRIMARY KEY,
    currency_code VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE warehouse.dimension_rating_methodologies_applied (
    rating_methodology_applied_id SERIAL PRIMARY KEY,
    rating_methodology_applied_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE warehouse.dimension_segmentation_criteria (
    segmentation_criteria_id SERIAL PRIMARY KEY,
    segmentation_criteria_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE warehouse.dimension_industry_risk_types (
    industry_risk_type_id SERIAL PRIMARY KEY,
    industry_risk_type_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE warehouse.dimension_companies (
    company_id INT NOT NULL,
    company_surrogate_key SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,

    sector_id INT NOT NULL,
    country_id INT NOT NULL,
    currency_id INT NOT NULL,

    accounting_principles VARCHAR(255) NOT NULL,
    end_of_business_month VARCHAR(20) NOT NULL,

    valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    valid_to TIMESTAMP WITH TIME ZONE DEFAULT 'infinity' NOT NULL,
    is_current BOOLEAN DEFAULT TRUE NOT NULL,

    CONSTRAINT fk_company_sector FOREIGN KEY (sector_id)
        REFERENCES warehouse.dimension_sectors(sector_id),
    CONSTRAINT fk_company_country FOREIGN KEY (country_id)
        REFERENCES warehouse.dimension_countries(country_id),
    CONSTRAINT fk_company_currency FOREIGN KEY (currency_id)
        REFERENCES warehouse.dimension_currencies(currency_id)
);

CREATE UNIQUE INDEX uq_dimension_companies_current
    ON warehouse.dimension_companies(company_id)
    WHERE is_current = TRUE;

-- Snapshot fact at upload/version grain.
-- Volatile assessment outputs live here (not as dimensions).
CREATE TABLE warehouse.fact_company_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    upload_id INT NOT NULL,
    company_surrogate_key INT NOT NULL,

    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    snapshot_status VARCHAR(50) DEFAULT 'success' NOT NULL,

    segmentation_criteria_id INT NOT NULL,

    -- Business risk outputs (versioned assessment values)
    business_risk_profile VARCHAR(50) NOT NULL,
    blended_industry_risk_profile VARCHAR(50) NOT NULL,
    competitive_positioning VARCHAR(50) NOT NULL,
    market_share VARCHAR(50) NOT NULL,
    diversification VARCHAR(50) NOT NULL,
    operating_profitability VARCHAR(50) NOT NULL,
    sector_or_company_specific_factor_1 VARCHAR(50),
    sector_or_company_specific_factor_2 VARCHAR(50),

    -- Financial risk outputs (versioned assessment values)
    financial_risk_profile VARCHAR(50) NOT NULL,
    leverage VARCHAR(50) NOT NULL,
    interest_cover VARCHAR(50) NOT NULL,
    cash_flow_cover VARCHAR(50) NOT NULL,
    liquidity_assessment VARCHAR(50) NOT NULL,

    valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    valid_to TIMESTAMP WITH TIME ZONE DEFAULT 'infinity' NOT NULL,

    CONSTRAINT fk_snapshot_upload FOREIGN KEY (upload_id)
        REFERENCES warehouse.upload_logs(upload_id),
    CONSTRAINT fk_snapshot_company FOREIGN KEY (company_surrogate_key)
        REFERENCES warehouse.dimension_companies(company_surrogate_key),
    CONSTRAINT fk_snapshot_segmentation FOREIGN KEY (segmentation_criteria_id)
        REFERENCES warehouse.dimension_segmentation_criteria(segmentation_criteria_id)
);

-- Many-to-many research methodologies per company snapshot
CREATE TABLE warehouse.bridge_company_snapshot_research_methodology (
    snapshot_id INT NOT NULL,
    rating_methodology_applied_id INT NOT NULL,
    PRIMARY KEY (snapshot_id, rating_methodology_applied_id),
    CONSTRAINT fk_bcsrm_snapshot FOREIGN KEY (snapshot_id)
        REFERENCES warehouse.fact_company_snapshots(snapshot_id),
    CONSTRAINT fk_bcsrm_methodology FOREIGN KEY (rating_methodology_applied_id)
        REFERENCES warehouse.dimension_rating_methodologies_applied(rating_methodology_applied_id)
);

-- Many-to-many industry risks per company snapshot + versioned score/weight
CREATE TABLE warehouse.bridge_company_snapshot_industry_risks (
    snapshot_id INT NOT NULL,
    industry_risk_type_id INT NOT NULL,
    industry_risk_score VARCHAR(50) NOT NULL,
    industry_weight NUMERIC(6,4) NOT NULL CHECK (industry_weight BETWEEN 0 AND 1),
    PRIMARY KEY (snapshot_id, industry_risk_type_id),
    CONSTRAINT fk_bcsir_snapshot FOREIGN KEY (snapshot_id)
        REFERENCES warehouse.fact_company_snapshots(snapshot_id),
    CONSTRAINT fk_bcsir_risk_type FOREIGN KEY (industry_risk_type_id)
        REFERENCES warehouse.dimension_industry_risk_types(industry_risk_type_id)
);

-- Time-series numeric metrics fact (per snapshot x year)
CREATE TABLE warehouse.fact_scope_credit_metrics (
    credit_metric_id SERIAL PRIMARY KEY,
    snapshot_id INT NOT NULL,
    metric_year VARCHAR(10) NOT NULL,

    scope_adjusted_ebitda_interest_cover NUMERIC(10,4),
    scope_adjusted_ebitda_interest_cover_status VARCHAR(20) NOT NULL DEFAULT 'numeric',
    scope_adjusted_debt_ebitda NUMERIC(10,4),
    scope_adjusted_debt_ebitda_status VARCHAR(20) NOT NULL DEFAULT 'numeric',
    scope_adjusted_ffo_debt NUMERIC(10,4),
    scope_adjusted_ffo_debt_status VARCHAR(20) NOT NULL DEFAULT 'numeric',
    scope_adjusted_loan_value NUMERIC(10,4),
    scope_adjusted_loan_value_status VARCHAR(20) NOT NULL DEFAULT 'numeric',
    scope_adjusted_focf_debt NUMERIC(10,4),
    scope_adjusted_focf_debt_status VARCHAR(20) NOT NULL DEFAULT 'numeric',
    liquidity NUMERIC(10,4),
    liquidity_status VARCHAR(20) NOT NULL DEFAULT 'numeric',

    -- BI-friendly explicit statuses for mixed source values.
    -- Suggested values: numeric, no_data, locked, missing, invalid.
    CONSTRAINT chk_ebitda_interest_cover_status
        CHECK (scope_adjusted_ebitda_interest_cover_status IN ('numeric', 'no_data', 'locked', 'missing', 'invalid')),
    CONSTRAINT chk_debt_ebitda_status
        CHECK (scope_adjusted_debt_ebitda_status IN ('numeric', 'no_data', 'locked', 'missing', 'invalid')),
    CONSTRAINT chk_ffo_debt_status
        CHECK (scope_adjusted_ffo_debt_status IN ('numeric', 'no_data', 'locked', 'missing', 'invalid')),
    CONSTRAINT chk_loan_value_status
        CHECK (scope_adjusted_loan_value_status IN ('numeric', 'no_data', 'locked', 'missing', 'invalid')),
    CONSTRAINT chk_focf_debt_status
        CHECK (scope_adjusted_focf_debt_status IN ('numeric', 'no_data', 'locked', 'missing', 'invalid')),
    CONSTRAINT chk_liquidity_status
        CHECK (liquidity_status IN ('numeric', 'no_data', 'locked', 'missing', 'invalid')),

    CONSTRAINT fk_metrics_snapshot FOREIGN KEY (snapshot_id)
        REFERENCES warehouse.fact_company_snapshots(snapshot_id),
    CONSTRAINT uq_metrics_snapshot_year UNIQUE (snapshot_id, metric_year)
);

CREATE INDEX idx_snapshots_upload_id
    ON warehouse.fact_company_snapshots(upload_id);
CREATE INDEX idx_snapshots_company_key
    ON warehouse.fact_company_snapshots(company_surrogate_key);
CREATE INDEX idx_snapshots_valid_window
    ON warehouse.fact_company_snapshots(valid_from, valid_to);

CREATE INDEX idx_bcsrm_snapshot_id
    ON warehouse.bridge_company_snapshot_research_methodology(snapshot_id);
CREATE INDEX idx_bcsrm_methodology_id
    ON warehouse.bridge_company_snapshot_research_methodology(rating_methodology_applied_id);

CREATE INDEX idx_bcsir_snapshot_id
    ON warehouse.bridge_company_snapshot_industry_risks(snapshot_id);
CREATE INDEX idx_bcsir_type_id
    ON warehouse.bridge_company_snapshot_industry_risks(industry_risk_type_id);

CREATE INDEX idx_metrics_snapshot_id
    ON warehouse.fact_scope_credit_metrics(snapshot_id);
CREATE INDEX idx_metrics_year
    ON warehouse.fact_scope_credit_metrics(metric_year);
