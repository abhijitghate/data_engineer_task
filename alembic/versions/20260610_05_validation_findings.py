"""add validation findings table for rule-level data quality lineage

Revision ID: 20260610_05
Revises: 20260608_04
Create Date: 2026-06-10
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260610_05"
down_revision: Union[str, None] = "20260608_04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.validation_findings (
            validation_finding_id SERIAL PRIMARY KEY,
            processed_file_id INT NOT NULL,
            run_id INT NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_checksum VARCHAR(64) NOT NULL,
            discussion_version VARCHAR(50) NOT NULL,
            rule_id VARCHAR(100) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            field_name VARCHAR(255) NOT NULL,
            message VARCHAR(2000) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            CONSTRAINT fk_validation_findings_processed_file
                FOREIGN KEY (processed_file_id)
                REFERENCES warehouse.processed_files(processed_file_id)
                ON DELETE CASCADE,
            CONSTRAINT chk_validation_findings_severity
                CHECK (severity IN ('error', 'warning'))
        );
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_validation_findings_processed_file_id
            ON warehouse.validation_findings(processed_file_id);
        CREATE INDEX IF NOT EXISTS idx_validation_findings_run_id
            ON warehouse.validation_findings(run_id);
        CREATE INDEX IF NOT EXISTS idx_validation_findings_checksum_version
            ON warehouse.validation_findings(file_checksum, discussion_version);
        CREATE INDEX IF NOT EXISTS idx_validation_findings_rule_id
            ON warehouse.validation_findings(rule_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS warehouse.validation_findings;")
