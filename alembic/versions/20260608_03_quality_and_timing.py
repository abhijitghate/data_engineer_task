"""add quality and timing columns for orchestration observability

Revision ID: 20260608_03
Revises: 20260608_02
Create Date: 2026-06-08
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260608_03"
down_revision: Union[str, None] = "20260608_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE warehouse.pipeline_runs
            ADD COLUMN IF NOT EXISTS quality_completeness_avg NUMERIC(6,4),
            ADD COLUMN IF NOT EXISTS quality_validity_avg NUMERIC(6,4),
            ADD COLUMN IF NOT EXISTS quality_warning_count INT DEFAULT 0 NOT NULL,
            ADD COLUMN IF NOT EXISTS extract_ms_total INT DEFAULT 0 NOT NULL,
            ADD COLUMN IF NOT EXISTS validate_ms_total INT DEFAULT 0 NOT NULL,
            ADD COLUMN IF NOT EXISTS transform_ms_total INT DEFAULT 0 NOT NULL,
            ADD COLUMN IF NOT EXISTS load_ms_total INT DEFAULT 0 NOT NULL,
            ADD COLUMN IF NOT EXISTS duration_ms INT;
        """
    )

    op.execute(
        """
        ALTER TABLE warehouse.processed_files
            ADD COLUMN IF NOT EXISTS quality_completeness_rate NUMERIC(6,4),
            ADD COLUMN IF NOT EXISTS quality_validity_rate NUMERIC(6,4),
            ADD COLUMN IF NOT EXISTS quality_warning_count INT,
            ADD COLUMN IF NOT EXISTS quality_warnings VARCHAR(2000),
            ADD COLUMN IF NOT EXISTS extract_ms INT,
            ADD COLUMN IF NOT EXISTS validate_ms INT,
            ADD COLUMN IF NOT EXISTS transform_ms INT,
            ADD COLUMN IF NOT EXISTS load_ms INT,
            ADD COLUMN IF NOT EXISTS total_ms INT;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE warehouse.processed_files
            DROP COLUMN IF EXISTS total_ms,
            DROP COLUMN IF EXISTS load_ms,
            DROP COLUMN IF EXISTS transform_ms,
            DROP COLUMN IF EXISTS validate_ms,
            DROP COLUMN IF EXISTS extract_ms,
            DROP COLUMN IF EXISTS quality_warnings,
            DROP COLUMN IF EXISTS quality_warning_count,
            DROP COLUMN IF EXISTS quality_validity_rate,
            DROP COLUMN IF EXISTS quality_completeness_rate;
        """
    )
    op.execute(
        """
        ALTER TABLE warehouse.pipeline_runs
            DROP COLUMN IF EXISTS duration_ms,
            DROP COLUMN IF EXISTS load_ms_total,
            DROP COLUMN IF EXISTS transform_ms_total,
            DROP COLUMN IF EXISTS validate_ms_total,
            DROP COLUMN IF EXISTS extract_ms_total,
            DROP COLUMN IF EXISTS quality_warning_count,
            DROP COLUMN IF EXISTS quality_validity_avg,
            DROP COLUMN IF EXISTS quality_completeness_avg;
        """
    )
