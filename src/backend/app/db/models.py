from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
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
