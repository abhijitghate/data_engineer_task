

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS applicationdatabase;



CREATE TABLE warehouse.upload_logs(
    upload_id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    discussion_version VARCHAR(50) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    upload_status VARCHAR(50) DEFAULT 'success' NOT NULL,
);

CREATE TABLE warehouse.dimension_sectors(
    sector_id SERIAL PRIMARY KEY,
    sector_name VARCHAR(255) NOT NULL UNIQUE
);


CREATE TABLE warehouse.dimension_rating_methodologies_applied(
    rating_methodology_applied_id SERIAL PRIMARY KEY,
    rating_methodology_applied_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE warehouse.dimension_industry_risks(
    industry_risk_id SERIAL PRIMARY KEY,
    industry_risk_name VARCHAR(255) NOT NULL,
    industry_risk_score VARCHAR(50) NOT NULL,
    industry_weight NUMERIC(5,2) CHECK (industry_weight BETWEEN 0 AND 100) NOT NULL,
);

CREATE TABLE warehouse.dimension_segmentation_criteria(
    segmentation_criteria_id SERIAL PRIMARY KEY,
    segmentation_criteria_name VARCHAR(255) NOT NULL UNIQUE
);


CREATE TABLE warehouse.dimension_companies(
    company_id INT NOT NULL, -- original company identifier from the source data
    company_surrogate_key SERIAL PRIMARY KEY, -- row identifier
    company_name VARCHAR(255) NOT NULL,
    reporting_currency VARCHAR(10) NOT NULL,
    country_of_origin VARCHAR(100) NOT NULL,
    accounting_principles VARCHAR(255) NOT NULL,
    end_of_business_month VARCHAR(20) NOT NULL,
);

CREATE TABLE warehouse.dimension_business_risk_profile(
    business_risk_profile_id SERIAL PRIMARY KEY,
    general_business_risk_profile VARCHAR(50) NOT NULL,
    blended_industry_risk_profile VARCHAR(50) NOT NULL,
    competitive_positioning VARCHAR(50) NOT NULL,
    market_share VARCHAR(50) NOT NULL,
    diversification VARCHAR(50) NOT NULL,
    operating_profitability VARCHAR(50) NOT NULL,
    sector_or_company_specific_factore_1 VARCHAR(50),
    sector_or_company_specific_factor_2 VARCHAR(50),
)

CREATE TABLE warehouse.dimension_financial_risk_profile(
    financial_risk_profile_id SERIAL PRIMARY KEY,
    general_financial_risk_profile VARCHAR(50) NOT NULL,
    leverage VARCHAR(50) NOT NULL,
    interest_cover VARCHAR(50) NOT NULL,
    cash_flow_cover VARCHAR(50) NOT NULL,
    liquidity VARCHAR(50) NOT NULL,
)

CREATE TABLE warehouse.dimension_scope_credit_metrics(
    credit_metric_id SERIAL PRIMARY KEY,
    company_surrogate_key INT NOT NULL,
    scope_adjusted_ebitda_interest_cover NUMERIC(5,2),   
    year VARCHAR(10) NOT NULL,
    scope_adjusted_debt_ebitda NUMERIC(5,2) CHECK (scope_adjusted_debt_ebitda BETWEEN 0 AND 100),
    scope_adjusted_ffo_debt NUMERIC(5,2) CHECK (scope_adjusted_ffo_debt BETWEEN 0 AND 100),
    scope_adjusted_loan_value NUMERIC(5,2) CHECK (scope_adjusted_loan_value BETWEEN 0 AND 100),
    scope_adjusted_focf_debt NUMERIC(5,2) CHECK (scope_adjusted_focf_debt BETWEEN 0 AND 100),
    liquidity NUMERIC(5,2) CHECK (liquidity BETWEEN 0 AND 100)
)

CREATE TABLE warehouse.ingestion_activities(
    ingestion_id SERIAL PRIMARY KEY,
    upload_id INT NOT NULL,
    CONSTRAINT fk_upload FOREIGN KEY (upload_id) REFERENCES warehouse.upload_logs(upload_id),
    
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ingestion_status VARCHAR(50) DEFAULT 'success' NOT NULL,

    company_surrogate_key INT NOT NULL,
    CONSTRAINT fk_company_surrogate FOREIGN KEY (company_surrogate_key) REFERENCES warehouse.dimension_companies(company_surrogate_key),
    
    company_id INT NOT NULL,
    CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES warehouse.dimension_companies(company_id),
    
    sector_id INT NOT NULL,
    CONSTRAINT fk_sector FOREIGN KEY (sector_id) REFERENCES warehouse.dimension_sectors(sector_id),
    
    rating_methodology_applied_ids INT[] NOT NULL,
    
    industry_risk_id INT[] NOT NULL,
    
    segmentation_criteria_id INT NOT NULL,
    CONSTRAINT fk_segmentation_criteria FOREIGN KEY (segmentation_criteria_id) REFERENCES warehouse.dimension_segmentation_criteria(segmentation_criteria_id),
    
    business_risk_profile_id INT NOT NULL,
    CONSTRAINT fk_business_risk_profile FOREIGN KEY (business_risk_profile_id) REFERENCES warehouse.dimension_business_risk_profile(business_risk_profile_id),

    financial_risk_profile_id INT NOT NULL,
    CONSTRAINT fk_financial_risk_profile FOREIGN KEY (financial_risk_profile_id) REFERENCES warehouse.dimension_financial_risk_profile(financial_risk_profile_id),
    
    credit_metric_id INT NOT NULL,
    CONSTRAINT fk_credit_metric FOREIGN KEY (credit_metric_id) REFERENCES warehouse.dimension_scope_credit_metrics(credit_metric_id),
    
    valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    valid_to TIMESTAMP WITH TIME ZONE DEFAULT 'infinity' NOT NULL,
    
)