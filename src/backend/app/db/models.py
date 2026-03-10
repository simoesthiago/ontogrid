from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "source"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    authority_type: Mapped[str] = mapped_column(String(64))
    refresh_strategy: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    datasets: Mapped[list["Dataset"]] = relationship(back_populates="source")
    aliases: Mapped[list["EntityAlias"]] = relationship(back_populates="source")


class Dataset(Base):
    __tablename__ = "dataset"
    __table_args__ = (UniqueConstraint("source_id", "code", name="uq_dataset_source_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("source.id"), index=True)
    code: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(64), index=True)
    granularity: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str] = mapped_column(Text())
    schema_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    refresh_frequency: Mapped[str] = mapped_column(String(64))
    latest_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("dataset_version.id", use_alter=True, name="fk_dataset_latest_version"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    source: Mapped[Source] = relationship(back_populates="datasets")
    versions: Mapped[list["DatasetVersion"]] = relationship(
        back_populates="dataset",
        foreign_keys="DatasetVersion.dataset_id",
        order_by="desc(DatasetVersion.published_at)",
    )
    latest_version: Mapped["DatasetVersion | None"] = relationship(foreign_keys=[latest_version_id], post_update=True)
    refresh_jobs: Mapped[list["RefreshJob"]] = relationship(back_populates="dataset")
    metric_series: Mapped[list["MetricSeries"]] = relationship(back_populates="dataset")


class DatasetVersion(Base):
    __tablename__ = "dataset_version"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("dataset.id"), index=True)
    label: Mapped[str] = mapped_column(String(128))
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    coverage_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    coverage_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    row_count: Mapped[int] = mapped_column(Integer())
    schema_version: Mapped[str] = mapped_column(String(64))
    checksum: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), index=True)
    lineage: Mapped[dict] = mapped_column(JSON, default=dict)

    dataset: Mapped[Dataset] = relationship(back_populates="versions", foreign_keys=[dataset_id])
    relations: Mapped[list["Relation"]] = relationship(back_populates="dataset_version")
    observations: Mapped[list["Observation"]] = relationship(back_populates="dataset_version")
    insight_snapshots: Mapped[list["InsightSnapshot"]] = relationship(back_populates="dataset_version")


class RefreshJob(Base):
    __tablename__ = "refresh_job"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("dataset.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(64))
    trigger_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), index=True)
    rows_read: Mapped[int] = mapped_column(Integer(), default=0)
    rows_written: Mapped[int] = mapped_column(Integer(), default=0)
    error_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    published_version_id: Mapped[str | None] = mapped_column(ForeignKey("dataset_version.id"), nullable=True)

    dataset: Mapped[Dataset] = relationship(back_populates="refresh_jobs")
    published_version: Mapped[DatasetVersion | None] = relationship(foreign_keys=[published_version_id])


class Entity(Base):
    __tablename__ = "entity"
    __table_args__ = (
        UniqueConstraint("entity_type", "canonical_code", name="uq_entity_type_canonical_code"),
        Index("ix_entity_entity_type_name", "entity_type", "name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    canonical_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    jurisdiction: Mapped[str] = mapped_column(String(64), default="BR")
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    aliases: Mapped[list["EntityAlias"]] = relationship(back_populates="entity")
    outgoing_relations: Mapped[list["Relation"]] = relationship(
        back_populates="source_entity",
        foreign_keys="Relation.source_entity_id",
    )
    incoming_relations: Mapped[list["Relation"]] = relationship(
        back_populates="target_entity",
        foreign_keys="Relation.target_entity_id",
    )
    observations: Mapped[list["Observation"]] = relationship(back_populates="entity")


class EntityAlias(Base):
    __tablename__ = "entity_alias"
    __table_args__ = (
        UniqueConstraint("source_id", "external_code", name="uq_entity_alias_source_external_code"),
        Index("ix_entity_alias_source_alias_name", "source_id", "alias_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_id: Mapped[str] = mapped_column(ForeignKey("entity.id"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("source.id"), index=True)
    external_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    alias_name: Mapped[str] = mapped_column(String(255))
    confidence: Mapped[float | None] = mapped_column(Float(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    entity: Mapped[Entity] = relationship(back_populates="aliases")
    source: Mapped[Source] = relationship(back_populates="aliases")


class Relation(Base):
    __tablename__ = "relation"
    __table_args__ = (
        UniqueConstraint(
            "dataset_version_id",
            "relation_type",
            "source_entity_id",
            "target_entity_id",
            name="uq_relation_dataset_version_type_pair",
        ),
        Index("ix_relation_source_target", "source_entity_id", "target_entity_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(ForeignKey("dataset_version.id"), index=True)
    relation_type: Mapped[str] = mapped_column(String(64), index=True)
    source_entity_id: Mapped[str] = mapped_column(ForeignKey("entity.id"), index=True)
    target_entity_id: Mapped[str] = mapped_column(ForeignKey("entity.id"), index=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)

    dataset_version: Mapped[DatasetVersion] = relationship(back_populates="relations")
    source_entity: Mapped[Entity] = relationship(
        back_populates="outgoing_relations",
        foreign_keys=[source_entity_id],
    )
    target_entity: Mapped[Entity] = relationship(
        back_populates="incoming_relations",
        foreign_keys=[target_entity_id],
    )


class MetricSeries(Base):
    __tablename__ = "metric_series"
    __table_args__ = (
        UniqueConstraint("dataset_id", "metric_code", "entity_type", name="uq_metric_series_dataset_metric_entity_type"),
        Index("ix_metric_series_dataset_metric", "dataset_id", "metric_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("dataset.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    metric_code: Mapped[str] = mapped_column(String(128))
    metric_name: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str] = mapped_column(String(64))
    temporal_granularity: Mapped[str] = mapped_column(String(32))
    dimensions: Mapped[dict] = mapped_column(JSON, default=dict)
    latest_observation_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    dataset: Mapped[Dataset] = relationship(back_populates="metric_series")
    observations: Mapped[list["Observation"]] = relationship(back_populates="series")


class Observation(Base):
    __tablename__ = "observation"
    __table_args__ = (
        Index("ix_observation_series_entity_time", "series_id", "entity_id", "time"),
    )

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    series_id: Mapped[str] = mapped_column(ForeignKey("metric_series.id"), primary_key=True)
    entity_id: Mapped[str] = mapped_column(ForeignKey("entity.id"), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(ForeignKey("dataset_version.id"), primary_key=True)
    value_numeric: Mapped[float | None] = mapped_column(Float(), nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    quality_flag: Mapped[str] = mapped_column(String(32), default="published")
    dimensions: Mapped[dict] = mapped_column(JSON, default=dict)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    series: Mapped[MetricSeries] = relationship(back_populates="observations")
    entity: Mapped[Entity] = relationship(back_populates="observations")
    dataset_version: Mapped[DatasetVersion] = relationship(back_populates="observations")


class InsightSnapshot(Base):
    __tablename__ = "insight_snapshot"
    __table_args__ = (
        Index("ix_insight_snapshot_scope_generated", "scope_type", "generated_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_type: Mapped[str] = mapped_column(String(32), index=True)
    scope_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text())
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    dataset_version_id: Mapped[str | None] = mapped_column(ForeignKey("dataset_version.id"), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    dataset_version: Mapped[DatasetVersion | None] = relationship(back_populates="insight_snapshots")


class CopilotTrace(Base):
    __tablename__ = "copilot_trace"
    __table_args__ = (
        Index("ix_copilot_trace_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    question: Mapped[str] = mapped_column(Text())
    scope: Mapped[dict] = mapped_column(JSON, default=dict)
    answer_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
