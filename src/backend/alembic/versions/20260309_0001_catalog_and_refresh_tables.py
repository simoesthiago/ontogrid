from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260309_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("authority_type", sa.String(length=64), nullable=False),
        sa.Column("refresh_strategy", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_source_code", "source", ["code"], unique=False)
    op.create_index("ix_source_status", "source", ["status"], unique=False)

    op.create_table(
        "dataset",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("domain", sa.String(length=64), nullable=False),
        sa.Column("granularity", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("schema_summary", sa.JSON(), nullable=False),
        sa.Column("refresh_frequency", sa.String(length=64), nullable=False),
        sa.Column("latest_version_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "code", name="uq_dataset_source_code"),
    )
    op.create_index("ix_dataset_domain", "dataset", ["domain"], unique=False)
    op.create_index("ix_dataset_granularity", "dataset", ["granularity"], unique=False)
    op.create_index("ix_dataset_source_id", "dataset", ["source_id"], unique=False)

    op.create_table(
        "dataset_version",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("dataset_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("coverage_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("coverage_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("schema_version", sa.String(length=64), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("lineage", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dataset_version_dataset_id", "dataset_version", ["dataset_id"], unique=False)
    op.create_index("ix_dataset_version_status", "dataset_version", ["status"], unique=False)

    op.create_foreign_key(
        "fk_dataset_latest_version",
        "dataset",
        "dataset_version",
        ["latest_version_id"],
        ["id"],
    )

    op.create_table(
        "refresh_job",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("dataset_id", sa.String(length=36), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("trigger_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rows_read", sa.Integer(), nullable=False),
        sa.Column("rows_written", sa.Integer(), nullable=False),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_version_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"]),
        sa.ForeignKeyConstraint(["published_version_id"], ["dataset_version.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_refresh_job_created_at", "refresh_job", ["created_at"], unique=False)
    op.create_index("ix_refresh_job_dataset_id", "refresh_job", ["dataset_id"], unique=False)
    op.create_index("ix_refresh_job_status", "refresh_job", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_refresh_job_status", table_name="refresh_job")
    op.drop_index("ix_refresh_job_dataset_id", table_name="refresh_job")
    op.drop_index("ix_refresh_job_created_at", table_name="refresh_job")
    op.drop_table("refresh_job")
    op.drop_constraint("fk_dataset_latest_version", "dataset", type_="foreignkey")
    op.drop_index("ix_dataset_version_status", table_name="dataset_version")
    op.drop_index("ix_dataset_version_dataset_id", table_name="dataset_version")
    op.drop_table("dataset_version")
    op.drop_index("ix_dataset_source_id", table_name="dataset")
    op.drop_index("ix_dataset_granularity", table_name="dataset")
    op.drop_index("ix_dataset_domain", table_name="dataset")
    op.drop_table("dataset")
    op.drop_index("ix_source_status", table_name="source")
    op.drop_index("ix_source_code", table_name="source")
    op.drop_table("source")
