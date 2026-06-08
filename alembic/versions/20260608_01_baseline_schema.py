"""baseline schema and serving views

Revision ID: 20260608_01
Revises:
Create Date: 2026-06-08
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260608_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS staging;")
    op.execute("CREATE SCHEMA IF NOT EXISTS warehouse;")
    op.execute("CREATE SCHEMA IF NOT EXISTS applicationdatabase;")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.upload_logs (
            upload_id SERIAL PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            storage_path VARCHAR(255) NOT NULL,
            discussion_version VARCHAR(50) NOT NULL,
            uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            upload_status VARCHAR(50) DEFAULT 'success' NOT NULL,
            file_checksum VARCHAR(64) NOT NULL UNIQUE
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.dimension_sectors (
            sector_id SERIAL PRIMARY KEY,
            sector_name VARCHAR(255) NOT NULL UNIQUE
        );
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.dimension_countries (
            country_id SERIAL PRIMARY KEY,
            country_name VARCHAR(100) NOT NULL UNIQUE
        );
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.dimension_currencies (
            currency_id SERIAL PRIMARY KEY,
            currency_code VARCHAR(10) NOT NULL UNIQUE
        );
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.dimension_rating_methodologies_applied (
            rating_methodology_applied_id SERIAL PRIMARY KEY,
            rating_methodology_applied_name VARCHAR(255) NOT NULL UNIQUE
        );
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.dimension_segmentation_criteria (
            segmentation_criteria_id SERIAL PRIMARY KEY,
            segmentation_criteria_name VARCHAR(255) NOT NULL UNIQUE
        );
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.dimension_industry_risk_types (
            industry_risk_type_id SERIAL PRIMARY KEY,
            industry_risk_type_name VARCHAR(255) NOT NULL UNIQUE
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.dimension_companies (
            company_id INT NOT NULL,
            company_version_id SERIAL PRIMARY KEY,
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
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.fact_company_snapshots (
            snapshot_id SERIAL PRIMARY KEY,
            upload_id INT NOT NULL,
            company_version_id INT NOT NULL,
            ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            snapshot_status VARCHAR(50) DEFAULT 'success' NOT NULL,
            segmentation_criteria_id INT NOT NULL,
            business_risk_profile VARCHAR(50) NOT NULL,
            blended_industry_risk_profile VARCHAR(50) NOT NULL,
            competitive_positioning VARCHAR(50) NOT NULL,
            market_share VARCHAR(50) NOT NULL,
            diversification VARCHAR(50) NOT NULL,
            operating_profitability VARCHAR(50) NOT NULL,
            sector_or_company_specific_factor_1 VARCHAR(50),
            sector_or_company_specific_factor_2 VARCHAR(50),
            financial_risk_profile VARCHAR(50) NOT NULL,
            leverage VARCHAR(50) NOT NULL,
            interest_cover VARCHAR(50) NOT NULL,
            cash_flow_cover VARCHAR(50) NOT NULL,
            liquidity_assessment VARCHAR(50) NOT NULL,
            valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            valid_to TIMESTAMP WITH TIME ZONE DEFAULT 'infinity' NOT NULL,
            CONSTRAINT fk_snapshot_upload FOREIGN KEY (upload_id)
                REFERENCES warehouse.upload_logs(upload_id),
            CONSTRAINT fk_snapshot_company FOREIGN KEY (company_version_id)
                REFERENCES warehouse.dimension_companies(company_version_id),
            CONSTRAINT fk_snapshot_segmentation FOREIGN KEY (segmentation_criteria_id)
                REFERENCES warehouse.dimension_segmentation_criteria(segmentation_criteria_id)
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.bridge_company_snapshot_research_methodology (
            snapshot_id INT NOT NULL,
            rating_methodology_applied_id INT NOT NULL,
            PRIMARY KEY (snapshot_id, rating_methodology_applied_id),
            CONSTRAINT fk_bcsrm_snapshot FOREIGN KEY (snapshot_id)
                REFERENCES warehouse.fact_company_snapshots(snapshot_id),
            CONSTRAINT fk_bcsrm_methodology FOREIGN KEY (rating_methodology_applied_id)
                REFERENCES warehouse.dimension_rating_methodologies_applied(rating_methodology_applied_id)
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.bridge_company_snapshot_industry_risks (
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
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.fact_scope_credit_metrics (
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
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'warehouse'
                  AND table_name = 'dimension_companies'
                  AND column_name = 'company_surrogate_key'
            ) THEN
                ALTER TABLE warehouse.dimension_companies
                    RENAME COLUMN company_surrogate_key TO company_version_id;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'warehouse'
                  AND table_name = 'fact_company_snapshots'
                  AND column_name = 'company_surrogate_key'
            ) THEN
                ALTER TABLE warehouse.fact_company_snapshots
                    DROP CONSTRAINT IF EXISTS fk_snapshot_company;
                ALTER TABLE warehouse.fact_company_snapshots
                    RENAME COLUMN company_surrogate_key TO company_version_id;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'fk_snapshot_company'
                  AND conrelid = 'warehouse.fact_company_snapshots'::regclass
            ) THEN
                ALTER TABLE warehouse.fact_company_snapshots
                    ADD CONSTRAINT fk_snapshot_company
                    FOREIGN KEY (company_version_id)
                    REFERENCES warehouse.dimension_companies(company_version_id);
            END IF;
        END $$;
        """
    )

    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_dimension_companies_current
            ON warehouse.dimension_companies(company_id)
            WHERE is_current = TRUE;
        CREATE INDEX IF NOT EXISTS idx_snapshots_upload_id
            ON warehouse.fact_company_snapshots(upload_id);
        CREATE INDEX IF NOT EXISTS idx_snapshots_company_key
            ON warehouse.fact_company_snapshots(company_version_id);
        CREATE INDEX IF NOT EXISTS idx_snapshots_valid_window
            ON warehouse.fact_company_snapshots(valid_from, valid_to);
        CREATE INDEX IF NOT EXISTS idx_bcsrm_snapshot_id
            ON warehouse.bridge_company_snapshot_research_methodology(snapshot_id);
        CREATE INDEX IF NOT EXISTS idx_bcsrm_methodology_id
            ON warehouse.bridge_company_snapshot_research_methodology(rating_methodology_applied_id);
        CREATE INDEX IF NOT EXISTS idx_bcsir_snapshot_id
            ON warehouse.bridge_company_snapshot_industry_risks(snapshot_id);
        CREATE INDEX IF NOT EXISTS idx_bcsir_type_id
            ON warehouse.bridge_company_snapshot_industry_risks(industry_risk_type_id);
        CREATE INDEX IF NOT EXISTS idx_metrics_snapshot_id
            ON warehouse.fact_scope_credit_metrics(snapshot_id);
        CREATE INDEX IF NOT EXISTS idx_metrics_year
            ON warehouse.fact_scope_credit_metrics(metric_year);
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW applicationdatabase.v_company_current_metadata AS
        SELECT
            c.company_id,
            c.company_version_id,
            c.company_name,
            s.sector_name,
            co.country_name,
            cu.currency_code,
            c.accounting_principles,
            c.end_of_business_month,
            c.valid_from AS company_valid_from,
            c.valid_to AS company_valid_to,
            c.is_current AS is_current_company_version
        FROM warehouse.dimension_companies c
        JOIN warehouse.dimension_sectors s
            ON s.sector_id = c.sector_id
        JOIN warehouse.dimension_countries co
            ON co.country_id = c.country_id
        JOIN warehouse.dimension_currencies cu
            ON cu.currency_id = c.currency_id
        WHERE c.is_current = TRUE;

        CREATE OR REPLACE VIEW applicationdatabase.v_company_versions AS
        SELECT
            c.company_id,
            c.company_version_id,
            c.company_name,
            s.sector_name,
            co.country_name,
            cu.currency_code,
            c.accounting_principles,
            c.end_of_business_month,
            c.valid_from AS company_valid_from,
            c.valid_to AS company_valid_to,
            c.is_current AS is_current_company_version,
            MIN(fs.ingested_at) AS first_snapshot_at,
            MAX(fs.ingested_at) AS last_snapshot_at,
            COUNT(fs.snapshot_id) AS snapshot_count
        FROM warehouse.dimension_companies c
        JOIN warehouse.dimension_sectors s
            ON s.sector_id = c.sector_id
        JOIN warehouse.dimension_countries co
            ON co.country_id = c.country_id
        JOIN warehouse.dimension_currencies cu
            ON cu.currency_id = c.currency_id
        LEFT JOIN warehouse.fact_company_snapshots fs
            ON fs.company_version_id = c.company_version_id
        GROUP BY
            c.company_id,
            c.company_version_id,
            c.company_name,
            s.sector_name,
            co.country_name,
            cu.currency_code,
            c.accounting_principles,
            c.end_of_business_month,
            c.valid_from,
            c.valid_to,
            c.is_current;

        CREATE OR REPLACE VIEW applicationdatabase.v_company_snapshots_enriched AS
        SELECT
            fs.snapshot_id,
            fs.upload_id,
            ul.file_name,
            ul.storage_path,
            ul.discussion_version,
            ul.uploaded_at,
            ul.upload_status,
            c.company_id,
            c.company_version_id,
            c.company_name,
            s.sector_name,
            co.country_name,
            cu.currency_code,
            c.accounting_principles,
            c.end_of_business_month,
            sc.segmentation_criteria_name,
            fs.business_risk_profile,
            fs.blended_industry_risk_profile,
            fs.competitive_positioning,
            fs.market_share,
            fs.diversification,
            fs.operating_profitability,
            fs.sector_or_company_specific_factor_1,
            fs.sector_or_company_specific_factor_2,
            fs.financial_risk_profile,
            fs.leverage,
            fs.interest_cover,
            fs.cash_flow_cover,
            fs.liquidity_assessment,
            fs.ingested_at AS snapshot_ingested_at,
            fs.valid_from AS snapshot_valid_from,
            fs.valid_to AS snapshot_valid_to,
            fs.snapshot_status
        FROM warehouse.fact_company_snapshots fs
        JOIN warehouse.upload_logs ul
            ON ul.upload_id = fs.upload_id
        JOIN warehouse.dimension_companies c
            ON c.company_version_id = fs.company_version_id
        JOIN warehouse.dimension_sectors s
            ON s.sector_id = c.sector_id
        JOIN warehouse.dimension_countries co
            ON co.country_id = c.country_id
        JOIN warehouse.dimension_currencies cu
            ON cu.currency_id = c.currency_id
        JOIN warehouse.dimension_segmentation_criteria sc
            ON sc.segmentation_criteria_id = fs.segmentation_criteria_id;

        CREATE OR REPLACE VIEW applicationdatabase.v_company_metric_history AS
        SELECT
            fs.snapshot_id,
            fs.upload_id,
            fs.company_id,
            fs.company_version_id,
            fs.company_name,
            fs.sector_name,
            fs.country_name,
            fs.currency_code,
            fs.discussion_version,
            fs.snapshot_ingested_at,
            m.metric_year,
            m.scope_adjusted_ebitda_interest_cover,
            m.scope_adjusted_ebitda_interest_cover_status,
            m.scope_adjusted_debt_ebitda,
            m.scope_adjusted_debt_ebitda_status,
            m.scope_adjusted_ffo_debt,
            m.scope_adjusted_ffo_debt_status,
            m.scope_adjusted_loan_value,
            m.scope_adjusted_loan_value_status,
            m.scope_adjusted_focf_debt,
            m.scope_adjusted_focf_debt_status,
            m.liquidity,
            m.liquidity_status
        FROM applicationdatabase.v_company_snapshots_enriched fs
        JOIN warehouse.fact_scope_credit_metrics m
            ON m.snapshot_id = fs.snapshot_id;

        CREATE OR REPLACE VIEW applicationdatabase.v_upload_stats AS
        SELECT
            ul.upload_id,
            ul.file_name,
            ul.storage_path,
            ul.discussion_version,
            ul.uploaded_at,
            ul.upload_status,
            ul.file_checksum,
            COUNT(DISTINCT fs.snapshot_id) AS snapshot_count,
            COUNT(DISTINCT c.company_id) AS company_count,
            COUNT(DISTINCT m.credit_metric_id) AS metric_row_count,
            MIN(fs.ingested_at) AS first_snapshot_at,
            MAX(fs.ingested_at) AS last_snapshot_at
        FROM warehouse.upload_logs ul
        LEFT JOIN warehouse.fact_company_snapshots fs
            ON fs.upload_id = ul.upload_id
        LEFT JOIN warehouse.dimension_companies c
            ON c.company_version_id = fs.company_version_id
        LEFT JOIN warehouse.fact_scope_credit_metrics m
            ON m.snapshot_id = fs.snapshot_id
        GROUP BY
            ul.upload_id,
            ul.file_name,
            ul.storage_path,
            ul.discussion_version,
            ul.uploaded_at,
            ul.upload_status,
            ul.file_checksum;
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS applicationdatabase.v_upload_stats;")
    op.execute("DROP VIEW IF EXISTS applicationdatabase.v_company_metric_history;")
    op.execute("DROP VIEW IF EXISTS applicationdatabase.v_company_snapshots_enriched;")
    op.execute("DROP VIEW IF EXISTS applicationdatabase.v_company_versions;")
    op.execute("DROP VIEW IF EXISTS applicationdatabase.v_company_current_metadata;")

    op.execute("DROP TABLE IF EXISTS warehouse.fact_scope_credit_metrics;")
    op.execute("DROP TABLE IF EXISTS warehouse.bridge_company_snapshot_industry_risks;")
    op.execute(
        "DROP TABLE IF EXISTS warehouse.bridge_company_snapshot_research_methodology;"
    )
    op.execute("DROP TABLE IF EXISTS warehouse.fact_company_snapshots;")
    op.execute("DROP TABLE IF EXISTS warehouse.dimension_companies;")
    op.execute("DROP TABLE IF EXISTS warehouse.dimension_industry_risk_types;")
    op.execute("DROP TABLE IF EXISTS warehouse.dimension_segmentation_criteria;")
    op.execute(
        "DROP TABLE IF EXISTS warehouse.dimension_rating_methodologies_applied;"
    )
    op.execute("DROP TABLE IF EXISTS warehouse.dimension_currencies;")
    op.execute("DROP TABLE IF EXISTS warehouse.dimension_countries;")
    op.execute("DROP TABLE IF EXISTS warehouse.dimension_sectors;")
    op.execute("DROP TABLE IF EXISTS warehouse.upload_logs;")
