from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection


revision = "20260309_0002"
down_revision = "20260309_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entity",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("canonical_code", sa.String(length=128), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("jurisdiction", sa.String(length=64), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entity_type", "canonical_code", name="uq_entity_type_canonical_code"),
    )
    op.create_index("ix_entity_entity_type", "entity", ["entity_type"], unique=False)
    op.create_index("ix_entity_entity_type_name", "entity", ["entity_type", "name"], unique=False)

    op.create_table(
        "entity_alias",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("external_code", sa.String(length=255), nullable=True),
        sa.Column("alias_name", sa.String(length=255), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "external_code", name="uq_entity_alias_source_external_code"),
    )
    op.create_index("ix_entity_alias_entity_id", "entity_alias", ["entity_id"], unique=False)
    op.create_index("ix_entity_alias_source_alias_name", "entity_alias", ["source_id", "alias_name"], unique=False)
    op.create_index("ix_entity_alias_source_id", "entity_alias", ["source_id"], unique=False)

    op.create_table(
        "metric_series",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("dataset_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("metric_code", sa.String(length=128), nullable=False),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=64), nullable=False),
        sa.Column("temporal_granularity", sa.String(length=32), nullable=False),
        sa.Column("dimensions", sa.JSON(), nullable=False),
        sa.Column("latest_observation_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dataset_id", "metric_code", "entity_type", name="uq_metric_series_dataset_metric_entity_type"),
    )
    op.create_index("ix_metric_series_dataset_id", "metric_series", ["dataset_id"], unique=False)
    op.create_index("ix_metric_series_dataset_metric", "metric_series", ["dataset_id", "metric_code"], unique=False)
    op.create_index("ix_metric_series_entity_type", "metric_series", ["entity_type"], unique=False)

    op.create_table(
        "relation",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=36), nullable=False),
        sa.Column("relation_type", sa.String(length=64), nullable=False),
        sa.Column("source_entity_id", sa.String(length=36), nullable=False),
        sa.Column("target_entity_id", sa.String(length=36), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_version.id"]),
        sa.ForeignKeyConstraint(["source_entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["target_entity_id"], ["entity.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "dataset_version_id",
            "relation_type",
            "source_entity_id",
            "target_entity_id",
            name="uq_relation_dataset_version_type_pair",
        ),
    )
    op.create_index("ix_relation_dataset_version_id", "relation", ["dataset_version_id"], unique=False)
    op.create_index("ix_relation_relation_type", "relation", ["relation_type"], unique=False)
    op.create_index("ix_relation_source_entity_id", "relation", ["source_entity_id"], unique=False)
    op.create_index("ix_relation_source_target", "relation", ["source_entity_id", "target_entity_id"], unique=False)
    op.create_index("ix_relation_target_entity_id", "relation", ["target_entity_id"], unique=False)

    op.create_table(
        "observation",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("series_id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=36), nullable=False),
        sa.Column("value_numeric", sa.Float(), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("quality_flag", sa.String(length=32), nullable=False),
        sa.Column("dimensions", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_version.id"]),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["series_id"], ["metric_series.id"]),
        sa.PrimaryKeyConstraint("time", "series_id", "entity_id", "dataset_version_id"),
    )
    op.create_index("ix_observation_series_entity_time", "observation", ["series_id", "entity_id", "time"], unique=False)
    _configure_observation_hypertable(op.get_bind())

    op.create_table(
        "insight_snapshot",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("scope_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=36), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_version.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_insight_snapshot_scope_generated", "insight_snapshot", ["scope_type", "generated_at"], unique=False)
    op.create_index("ix_insight_snapshot_scope_type", "insight_snapshot", ["scope_type"], unique=False)

    op.create_table(
        "copilot_trace",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("scope", sa.JSON(), nullable=False),
        sa.Column("answer_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_copilot_trace_created_at", "copilot_trace", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_copilot_trace_created_at", table_name="copilot_trace")
    op.drop_table("copilot_trace")
    op.drop_index("ix_insight_snapshot_scope_type", table_name="insight_snapshot")
    op.drop_index("ix_insight_snapshot_scope_generated", table_name="insight_snapshot")
    op.drop_table("insight_snapshot")
    op.drop_index("ix_observation_series_entity_time", table_name="observation")
    op.drop_table("observation")
    op.drop_index("ix_relation_target_entity_id", table_name="relation")
    op.drop_index("ix_relation_source_target", table_name="relation")
    op.drop_index("ix_relation_source_entity_id", table_name="relation")
    op.drop_index("ix_relation_relation_type", table_name="relation")
    op.drop_index("ix_relation_dataset_version_id", table_name="relation")
    op.drop_table("relation")
    op.drop_index("ix_metric_series_entity_type", table_name="metric_series")
    op.drop_index("ix_metric_series_dataset_metric", table_name="metric_series")
    op.drop_index("ix_metric_series_dataset_id", table_name="metric_series")
    op.drop_table("metric_series")
    op.drop_index("ix_entity_alias_source_id", table_name="entity_alias")
    op.drop_index("ix_entity_alias_source_alias_name", table_name="entity_alias")
    op.drop_index("ix_entity_alias_entity_id", table_name="entity_alias")
    op.drop_table("entity_alias")
    op.drop_index("ix_entity_entity_type_name", table_name="entity")
    op.drop_index("ix_entity_entity_type", table_name="entity")
    op.drop_table("entity")


def _configure_observation_hypertable(connection: Connection) -> None:
    if connection.dialect.name != "postgresql":
        return
    connection.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS timescaledb")
    connection.exec_driver_sql(
        "SELECT create_hypertable('observation', 'time', if_not_exists => TRUE, migrate_data => TRUE)"
    )
