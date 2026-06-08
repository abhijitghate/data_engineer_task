"""add pipeline run state and processed files tracking

Revision ID: 20260608_02
Revises: 20260608_01
Create Date: 2026-06-08
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260608_02"
down_revision: Union[str, None] = "20260608_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.pipeline_runs (
            run_id SERIAL PRIMARY KEY,
            discussion_version VARCHAR(50) NOT NULL,
            started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            finished_at TIMESTAMP WITH TIME ZONE,
            status VARCHAR(50) DEFAULT 'running' NOT NULL,
            files_total INT DEFAULT 0 NOT NULL,
            files_processed INT DEFAULT 0 NOT NULL,
            files_succeeded INT DEFAULT 0 NOT NULL,
            files_failed INT DEFAULT 0 NOT NULL,
            files_skipped INT DEFAULT 0 NOT NULL,
            error_summary VARCHAR(2000)
        );
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS warehouse.processed_files (
            processed_file_id SERIAL PRIMARY KEY,
            run_id INT NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            file_checksum VARCHAR(64) NOT NULL,
            discussion_version VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            upload_id INT,
            company_id INT,
            company_version_id INT,
            snapshot_id INT,
            error_message VARCHAR(2000),
            processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            CONSTRAINT fk_processed_files_run
                FOREIGN KEY (run_id) REFERENCES warehouse.pipeline_runs(run_id)
        );
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_processed_files_run_id
            ON warehouse.processed_files(run_id);
        CREATE INDEX IF NOT EXISTS idx_processed_files_checksum_version_status
            ON warehouse.processed_files(file_checksum, discussion_version, status);
        CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status_started
            ON warehouse.pipeline_runs(status, started_at DESC);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS warehouse.processed_files;")
    op.execute("DROP TABLE IF EXISTS warehouse.pipeline_runs;")
