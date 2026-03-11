from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260311_0004"
down_revision = "20260310_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "metric_series",
        sa.Column("semantic_value_type", sa.String(length=64), nullable=False, server_default="observed"),
    )
    op.add_column(
        "metric_series",
        sa.Column("reference_time_kind", sa.String(length=64), nullable=False, server_default="instant"),
    )
    op.create_index("ix_metric_series_semantic_value_type", "metric_series", ["semantic_value_type"], unique=False)
    op.create_index("ix_metric_series_reference_time_kind", "metric_series", ["reference_time_kind"], unique=False)

    op.execute(
        """
        UPDATE metric_series
        SET semantic_value_type = COALESCE(
            (SELECT semantic_value_type FROM series_registry WHERE series_registry.metric_series_id = metric_series.id),
            'observed'
        )
        """
    )
    op.execute(
        """
        UPDATE metric_series
        SET reference_time_kind = COALESCE(
            (SELECT reference_time_kind FROM series_registry WHERE series_registry.metric_series_id = metric_series.id),
            'instant'
        )
        """
    )

    with op.batch_alter_table("metric_series") as batch_op:
        batch_op.drop_constraint("uq_metric_series_dataset_metric_entity_type", type_="unique")
        batch_op.create_unique_constraint(
            "uq_metric_series_dataset_metric_semantics_entity_type",
            ["dataset_id", "metric_code", "entity_type", "semantic_value_type", "reference_time_kind"],
        )

    op.create_table(
        "harmonization_event",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("source_code", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("source_record_key", sa.String(length=255), nullable=False),
        sa.Column("decision", sa.String(length=64), nullable=False),
        sa.Column("match_rule", sa.String(length=64), nullable=False),
        sa.Column("matched_on", sa.JSON(), nullable=False),
        sa.Column("source_identity", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_version.id"]),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "dataset_version_id",
            "source_record_key",
            name="uq_harmonization_event_dataset_record",
        ),
    )
    op.create_index("ix_harmonization_event_created_at", "harmonization_event", ["created_at"], unique=False)
    op.create_index(
        "ix_harmonization_event_dataset_version_id",
        "harmonization_event",
        ["dataset_version_id"],
        unique=False,
    )
    op.create_index("ix_harmonization_event_entity_created", "harmonization_event", ["entity_id", "created_at"], unique=False)
    op.create_index("ix_harmonization_event_entity_id", "harmonization_event", ["entity_id"], unique=False)
    op.create_index("ix_harmonization_event_entity_type", "harmonization_event", ["entity_type"], unique=False)
    op.create_index("ix_harmonization_event_match_rule", "harmonization_event", ["match_rule"], unique=False)
    op.create_index("ix_harmonization_event_source_code", "harmonization_event", ["source_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_harmonization_event_source_code", table_name="harmonization_event")
    op.drop_index("ix_harmonization_event_match_rule", table_name="harmonization_event")
    op.drop_index("ix_harmonization_event_entity_type", table_name="harmonization_event")
    op.drop_index("ix_harmonization_event_entity_id", table_name="harmonization_event")
    op.drop_index("ix_harmonization_event_entity_created", table_name="harmonization_event")
    op.drop_index("ix_harmonization_event_dataset_version_id", table_name="harmonization_event")
    op.drop_index("ix_harmonization_event_created_at", table_name="harmonization_event")
    op.drop_table("harmonization_event")

    with op.batch_alter_table("metric_series") as batch_op:
        batch_op.drop_constraint("uq_metric_series_dataset_metric_semantics_entity_type", type_="unique")
        batch_op.create_unique_constraint(
            "uq_metric_series_dataset_metric_entity_type",
            ["dataset_id", "metric_code", "entity_type"],
        )

    op.drop_index("ix_metric_series_reference_time_kind", table_name="metric_series")
    op.drop_index("ix_metric_series_semantic_value_type", table_name="metric_series")
    op.drop_column("metric_series", "reference_time_kind")
    op.drop_column("metric_series", "semantic_value_type")
