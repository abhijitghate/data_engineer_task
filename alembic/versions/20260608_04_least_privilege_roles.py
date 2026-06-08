"""create least-privilege roles and grants

Revision ID: 20260608_04
Revises: 20260608_03
Create Date: 2026-06-08
"""

from __future__ import annotations

import os
from typing import Sequence, Union

from alembic import op


revision: str = "20260608_04"
down_revision: Union[str, None] = "20260608_03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _escape_sql_literal(value: str) -> str:
    return value.replace("'", "''")


def _create_login_role_if_password_present(role_name: str, password_env_key: str) -> None:
    password = os.getenv(password_env_key)
    if not password:
        return

    role = _escape_sql_literal(role_name)
    secret = _escape_sql_literal(password)
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                EXECUTE 'CREATE ROLE "{role}" LOGIN PASSWORD ''{secret}''';
            ELSE
                EXECUTE 'ALTER ROLE "{role}" WITH LOGIN PASSWORD ''{secret}''';
            END IF;
        END $$;
        """
    )


def upgrade() -> None:
    app_role = os.getenv("API_DB_USER", "scope_app_read")
    pipeline_role = os.getenv("PIPELINE_DB_USER", "scope_pipeline_write")

    # Permission roles own grants; login roles can be rotated independently.
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'scope_app_read_role') THEN
                CREATE ROLE scope_app_read_role NOLOGIN;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'scope_pipeline_write_role') THEN
                CREATE ROLE scope_pipeline_write_role NOLOGIN;
            END IF;
        END $$;
        """
    )

    _create_login_role_if_password_present(app_role, "API_DB_PASSWORD")
    _create_login_role_if_password_present(pipeline_role, "PIPELINE_DB_PASSWORD")

    op.execute(
        """
        GRANT USAGE ON SCHEMA warehouse TO scope_app_read_role, scope_pipeline_write_role;
        GRANT USAGE ON SCHEMA applicationdatabase TO scope_app_read_role, scope_pipeline_write_role;

        GRANT SELECT ON ALL TABLES IN SCHEMA warehouse TO scope_app_read_role;
        GRANT SELECT ON ALL TABLES IN SCHEMA applicationdatabase TO scope_app_read_role;

        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA warehouse TO scope_pipeline_write_role;
        GRANT SELECT ON ALL TABLES IN SCHEMA applicationdatabase TO scope_pipeline_write_role;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA warehouse TO scope_pipeline_write_role;

        ALTER DEFAULT PRIVILEGES IN SCHEMA warehouse
            GRANT SELECT ON TABLES TO scope_app_read_role;
        ALTER DEFAULT PRIVILEGES IN SCHEMA applicationdatabase
            GRANT SELECT ON TABLES TO scope_app_read_role;

        ALTER DEFAULT PRIVILEGES IN SCHEMA warehouse
            GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO scope_pipeline_write_role;
        ALTER DEFAULT PRIVILEGES IN SCHEMA applicationdatabase
            GRANT SELECT ON TABLES TO scope_pipeline_write_role;
        ALTER DEFAULT PRIVILEGES IN SCHEMA warehouse
            GRANT USAGE, SELECT ON SEQUENCES TO scope_pipeline_write_role;
        """
    )

    app_role_escaped = _escape_sql_literal(app_role)
    pipeline_role_escaped = _escape_sql_literal(pipeline_role)
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{app_role_escaped}') THEN
                EXECUTE 'GRANT scope_app_read_role TO "{app_role_escaped}"';
            END IF;

            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{pipeline_role_escaped}') THEN
                EXECUTE 'GRANT scope_pipeline_write_role TO "{pipeline_role_escaped}"';
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    app_role = os.getenv("API_DB_USER", "scope_app_read")
    pipeline_role = os.getenv("PIPELINE_DB_USER", "scope_pipeline_write")
    app_role_escaped = _escape_sql_literal(app_role)
    pipeline_role_escaped = _escape_sql_literal(pipeline_role)

    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{app_role_escaped}') THEN
                EXECUTE 'REVOKE scope_app_read_role FROM "{app_role_escaped}"';
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{pipeline_role_escaped}') THEN
                EXECUTE 'REVOKE scope_pipeline_write_role FROM "{pipeline_role_escaped}"';
            END IF;
        END $$;
        """
    )

    op.execute("DROP ROLE IF EXISTS scope_pipeline_write_role;")
    op.execute("DROP ROLE IF EXISTS scope_app_read_role;")
