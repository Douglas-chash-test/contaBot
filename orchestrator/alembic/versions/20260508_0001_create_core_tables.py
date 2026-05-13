"""create core tables

Revision ID: 20260508_0001
Revises:
Create Date: 2026-05-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260508_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cnpj", sa.String(length=14), nullable=False),
        sa.Column("inscricao_estadual", sa.String(length=32), nullable=False),
        sa.Column("razao_social", sa.String(length=255), nullable=False),
        sa.Column("whatsapp_dest", sa.String(length=32), nullable=False),
        sa.Column("api_key_hash", sa.String(length=255), nullable=False),
        sa.Column("erp_type", sa.String(length=64), nullable=False),
        sa.Column("db_type", sa.String(length=64), nullable=False),
        sa.Column(
            "config_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
    )
    op.create_index("ix_clients_cnpj", "clients", ["cnpj"], unique=True)

    op.create_table(
        "executions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("periodo", sa.String(length=7), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("log_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("error_details", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_executions_client_periodo",
        "executions",
        ["client_id", "periodo"],
        unique=False,
    )
    op.create_index("ix_executions_status", "executions", ["status"], unique=False)

    op.create_table(
        "commands",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("execution_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "result_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["executions.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_commands_execution_status",
        "commands",
        ["execution_id", "status"],
        unique=False,
    )

    op.create_table(
        "error_dictionary",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("error_code", sa.String(length=128), nullable=False),
        sa.Column(
            "context_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("solution_sql", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False),
    )
    op.create_index(
        "ix_error_dictionary_error_code",
        "error_dictionary",
        ["error_code"],
        unique=False,
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("execution_id", sa.Integer(), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("query_hash", sa.String(length=64), nullable=False),
        sa.Column("origin", sa.String(length=32), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["executions.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_audit_log_execution_id", "audit_log", ["execution_id"])
    op.create_index("ix_audit_log_query_hash", "audit_log", ["query_hash"])


def downgrade() -> None:
    op.drop_index("ix_audit_log_query_hash", table_name="audit_log")
    op.drop_index("ix_audit_log_execution_id", table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_index("ix_error_dictionary_error_code", table_name="error_dictionary")
    op.drop_table("error_dictionary")
    op.drop_index("ix_commands_execution_status", table_name="commands")
    op.drop_table("commands")
    op.drop_index("ix_executions_status", table_name="executions")
    op.drop_index("ix_executions_client_periodo", table_name="executions")
    op.drop_table("executions")
    op.drop_index("ix_clients_cnpj", table_name="clients")
    op.drop_table("clients")
