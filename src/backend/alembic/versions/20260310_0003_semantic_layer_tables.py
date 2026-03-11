from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260310_0003"
down_revision = "20260309_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "party_master",
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("tax_id", sa.String(length=32), nullable=True),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("trade_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("source_dataset_version_id", sa.String(length=36), nullable=False),
        sa.Column("lineage", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["source_dataset_version_id"], ["dataset_version.id"]),
        sa.PrimaryKeyConstraint("entity_id"),
    )
    op.create_index("ix_party_master_tax_id", "party_master", ["tax_id"], unique=False)
    op.create_index("ix_party_master_source_dataset_version_id", "party_master", ["source_dataset_version_id"], unique=False)

    op.create_table(
        "agent_profile_master",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("party_entity_id", sa.String(length=36), nullable=True),
        sa.Column("profile_kind", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.Column("source_code", sa.String(length=64), nullable=False),
        sa.Column("external_code", sa.String(length=255), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_dataset_version_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["party_entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["source_dataset_version_id"], ["dataset_version.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "entity_id",
            "profile_kind",
            "role",
            "source_code",
            "external_code",
            name="uq_agent_profile_master_identity",
        ),
    )
    op.create_index("ix_agent_profile_master_entity_id", "agent_profile_master", ["entity_id"], unique=False)
    op.create_index("ix_agent_profile_master_party_entity_id", "agent_profile_master", ["party_entity_id"], unique=False)
    op.create_index("ix_agent_profile_master_profile_kind", "agent_profile_master", ["profile_kind"], unique=False)
    op.create_index("ix_agent_profile_master_role", "agent_profile_master", ["role"], unique=False)
    op.create_index("ix_agent_profile_master_source_code", "agent_profile_master", ["source_code"], unique=False)
    op.create_index("ix_agent_profile_master_source_dataset_version_id", "agent_profile_master", ["source_dataset_version_id"], unique=False)

    op.create_table(
        "asset_master_generation",
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("ceg", sa.String(length=128), nullable=True),
        sa.Column("ons_plant_code", sa.String(length=128), nullable=True),
        sa.Column("source_type", sa.String(length=128), nullable=True),
        sa.Column("fuel_type", sa.String(length=128), nullable=True),
        sa.Column("installed_capacity_mw", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("municipality_entity_id", sa.String(length=36), nullable=True),
        sa.Column("subsystem_entity_id", sa.String(length=36), nullable=True),
        sa.Column("submarket_entity_id", sa.String(length=36), nullable=True),
        sa.Column("source_dataset_version_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["municipality_entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["submarket_entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["subsystem_entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["source_dataset_version_id"], ["dataset_version.id"]),
        sa.PrimaryKeyConstraint("entity_id"),
    )
    op.create_index("ix_asset_master_generation_ceg", "asset_master_generation", ["ceg"], unique=False)
    op.create_index("ix_asset_master_generation_ons_plant_code", "asset_master_generation", ["ons_plant_code"], unique=False)
    op.create_index("ix_asset_master_generation_municipality_entity_id", "asset_master_generation", ["municipality_entity_id"], unique=False)
    op.create_index("ix_asset_master_generation_submarket_entity_id", "asset_master_generation", ["submarket_entity_id"], unique=False)
    op.create_index("ix_asset_master_generation_subsystem_entity_id", "asset_master_generation", ["subsystem_entity_id"], unique=False)
    op.create_index("ix_asset_master_generation_source_dataset_version_id", "asset_master_generation", ["source_dataset_version_id"], unique=False)

    op.create_table(
        "asset_bridge_generation",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("asset_entity_id", sa.String(length=36), nullable=False),
        sa.Column("bridge_kind", sa.String(length=64), nullable=False),
        sa.Column("external_code", sa.String(length=255), nullable=False),
        sa.Column("source_code", sa.String(length=64), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_dataset_version_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["asset_entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["source_dataset_version_id"], ["dataset_version.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "asset_entity_id",
            "bridge_kind",
            "source_code",
            "external_code",
            name="uq_asset_bridge_generation_identity",
        ),
    )
    op.create_index("ix_asset_bridge_generation_asset_entity_id", "asset_bridge_generation", ["asset_entity_id"], unique=False)
    op.create_index("ix_asset_bridge_generation_bridge_kind", "asset_bridge_generation", ["bridge_kind"], unique=False)
    op.create_index("ix_asset_bridge_generation_source_code", "asset_bridge_generation", ["source_code"], unique=False)
    op.create_index("ix_asset_bridge_generation_source_dataset_version_id", "asset_bridge_generation", ["source_dataset_version_id"], unique=False)

    op.create_table(
        "geo_electric_master",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("geo_type", sa.String(length=64), nullable=False),
        sa.Column("ibge_code", sa.String(length=32), nullable=True),
        sa.Column("operator_code", sa.String(length=64), nullable=True),
        sa.Column("parent_entity_id", sa.String(length=36), nullable=True),
        sa.Column("mapped_entity_id", sa.String(length=36), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_dataset_version_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["mapped_entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["parent_entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["source_dataset_version_id"], ["dataset_version.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_geo_electric_master_entity_id", "geo_electric_master", ["entity_id"], unique=False)
    op.create_index("ix_geo_electric_master_geo_type", "geo_electric_master", ["geo_type"], unique=False)
    op.create_index("ix_geo_electric_master_ibge_code", "geo_electric_master", ["ibge_code"], unique=False)
    op.create_index("ix_geo_electric_master_operator_code", "geo_electric_master", ["operator_code"], unique=False)
    op.create_index("ix_geo_electric_master_parent_entity_id", "geo_electric_master", ["parent_entity_id"], unique=False)
    op.create_index("ix_geo_electric_master_mapped_entity_id", "geo_electric_master", ["mapped_entity_id"], unique=False)
    op.create_index("ix_geo_electric_master_source_dataset_version_id", "geo_electric_master", ["source_dataset_version_id"], unique=False)
    op.create_index("ix_geo_electric_master_entity_geo_type", "geo_electric_master", ["entity_id", "geo_type"], unique=False)

    op.create_table(
        "series_registry",
        sa.Column("metric_series_id", sa.String(length=36), nullable=False),
        sa.Column("semantic_value_type", sa.String(length=64), nullable=False),
        sa.Column("reference_time_kind", sa.String(length=64), nullable=False),
        sa.Column("target_entity_type", sa.String(length=64), nullable=False),
        sa.Column("unit", sa.String(length=64), nullable=False),
        sa.Column("source_dataset_version_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["metric_series_id"], ["metric_series.id"]),
        sa.ForeignKeyConstraint(["source_dataset_version_id"], ["dataset_version.id"]),
        sa.PrimaryKeyConstraint("metric_series_id"),
    )
    op.create_index("ix_series_registry_reference_time_kind", "series_registry", ["reference_time_kind"], unique=False)
    op.create_index("ix_series_registry_semantic_value_type", "series_registry", ["semantic_value_type"], unique=False)
    op.create_index("ix_series_registry_source_dataset_version_id", "series_registry", ["source_dataset_version_id"], unique=False)
    op.create_index("ix_series_registry_target_entity_type", "series_registry", ["target_entity_type"], unique=False)

    op.create_table(
        "evidence_registry",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_type", sa.String(length=64), nullable=False),
        sa.Column("scope_id", sa.String(length=255), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=36), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("series_id", sa.String(length=36), nullable=True),
        sa.Column("observation_selector", sa.JSON(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_version.id"]),
        sa.ForeignKeyConstraint(["entity_id"], ["entity.id"]),
        sa.ForeignKeyConstraint(["series_id"], ["metric_series.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evidence_registry_created_at", "evidence_registry", ["created_at"], unique=False)
    op.create_index("ix_evidence_registry_dataset_version_id", "evidence_registry", ["dataset_version_id"], unique=False)
    op.create_index("ix_evidence_registry_entity_created", "evidence_registry", ["entity_id", "created_at"], unique=False)
    op.create_index("ix_evidence_registry_entity_id", "evidence_registry", ["entity_id"], unique=False)
    op.create_index("ix_evidence_registry_scope", "evidence_registry", ["scope_type", "scope_id"], unique=False)
    op.create_index("ix_evidence_registry_scope_id", "evidence_registry", ["scope_id"], unique=False)
    op.create_index("ix_evidence_registry_scope_type", "evidence_registry", ["scope_type"], unique=False)
    op.create_index("ix_evidence_registry_series_id", "evidence_registry", ["series_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_evidence_registry_series_id", table_name="evidence_registry")
    op.drop_index("ix_evidence_registry_scope_type", table_name="evidence_registry")
    op.drop_index("ix_evidence_registry_scope_id", table_name="evidence_registry")
    op.drop_index("ix_evidence_registry_scope", table_name="evidence_registry")
    op.drop_index("ix_evidence_registry_entity_id", table_name="evidence_registry")
    op.drop_index("ix_evidence_registry_entity_created", table_name="evidence_registry")
    op.drop_index("ix_evidence_registry_dataset_version_id", table_name="evidence_registry")
    op.drop_index("ix_evidence_registry_created_at", table_name="evidence_registry")
    op.drop_table("evidence_registry")
    op.drop_index("ix_series_registry_target_entity_type", table_name="series_registry")
    op.drop_index("ix_series_registry_source_dataset_version_id", table_name="series_registry")
    op.drop_index("ix_series_registry_semantic_value_type", table_name="series_registry")
    op.drop_index("ix_series_registry_reference_time_kind", table_name="series_registry")
    op.drop_table("series_registry")
    op.drop_index("ix_geo_electric_master_entity_geo_type", table_name="geo_electric_master")
    op.drop_index("ix_geo_electric_master_source_dataset_version_id", table_name="geo_electric_master")
    op.drop_index("ix_geo_electric_master_mapped_entity_id", table_name="geo_electric_master")
    op.drop_index("ix_geo_electric_master_parent_entity_id", table_name="geo_electric_master")
    op.drop_index("ix_geo_electric_master_operator_code", table_name="geo_electric_master")
    op.drop_index("ix_geo_electric_master_ibge_code", table_name="geo_electric_master")
    op.drop_index("ix_geo_electric_master_geo_type", table_name="geo_electric_master")
    op.drop_index("ix_geo_electric_master_entity_id", table_name="geo_electric_master")
    op.drop_table("geo_electric_master")
    op.drop_index("ix_asset_bridge_generation_source_dataset_version_id", table_name="asset_bridge_generation")
    op.drop_index("ix_asset_bridge_generation_source_code", table_name="asset_bridge_generation")
    op.drop_index("ix_asset_bridge_generation_bridge_kind", table_name="asset_bridge_generation")
    op.drop_index("ix_asset_bridge_generation_asset_entity_id", table_name="asset_bridge_generation")
    op.drop_table("asset_bridge_generation")
    op.drop_index("ix_asset_master_generation_source_dataset_version_id", table_name="asset_master_generation")
    op.drop_index("ix_asset_master_generation_subsystem_entity_id", table_name="asset_master_generation")
    op.drop_index("ix_asset_master_generation_submarket_entity_id", table_name="asset_master_generation")
    op.drop_index("ix_asset_master_generation_municipality_entity_id", table_name="asset_master_generation")
    op.drop_index("ix_asset_master_generation_ons_plant_code", table_name="asset_master_generation")
    op.drop_index("ix_asset_master_generation_ceg", table_name="asset_master_generation")
    op.drop_table("asset_master_generation")
    op.drop_index("ix_agent_profile_master_source_dataset_version_id", table_name="agent_profile_master")
    op.drop_index("ix_agent_profile_master_source_code", table_name="agent_profile_master")
    op.drop_index("ix_agent_profile_master_role", table_name="agent_profile_master")
    op.drop_index("ix_agent_profile_master_profile_kind", table_name="agent_profile_master")
    op.drop_index("ix_agent_profile_master_party_entity_id", table_name="agent_profile_master")
    op.drop_index("ix_agent_profile_master_entity_id", table_name="agent_profile_master")
    op.drop_table("agent_profile_master")
    op.drop_index("ix_party_master_source_dataset_version_id", table_name="party_master")
    op.drop_index("ix_party_master_tax_id", table_name="party_master")
    op.drop_table("party_master")
