from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.domain import (
    validate_entity_type,
    validate_reference_time_kind,
    validate_relation_type,
    validate_semantic_value_type,
)
from app.db.models import (
    Dataset,
    DatasetVersion,
    EntityAlias,
    MetricSeries,
    Observation,
    RefreshJob,
    Relation,
    Source,
)
from app.ingestion import get_adapter
from app.ingestion.registry import has_adapter
from app.ingestion.base import ParsedDatasetPayload, ParsedEntityAlias, ParsedMetricSeries
from app.services.evidence_service import evidence_service
from app.services.catalog_service import to_iso8601
from app.services.graph_service import get_graph_service
from app.services.harmonization_service import harmonization_service
from app.services.insight_service import insight_service
from app.services.semantic_service import semantic_service

logger = logging.getLogger(__name__)


class RefreshService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory
        self._lock = Lock()

    def queue_refresh(self, dataset_id: str, trigger_type: str) -> RefreshJob:
        with self.session_factory() as session:
            dataset = session.get(Dataset, dataset_id)
            if dataset is None:
                raise ValueError(f"Dataset {dataset_id} not found")
            if not has_adapter(dataset.code):
                raise ValueError(f"Dataset {dataset.code} is cataloged but has no ingestion adapter")

            active_job = session.scalar(
                select(RefreshJob)
                .where(
                    RefreshJob.dataset_id == dataset_id,
                    RefreshJob.status.in_(("queued", "running")),
                )
                .order_by(RefreshJob.created_at.desc())
            )
            if active_job is not None:
                return active_job

            job = RefreshJob(
                id=str(uuid4()),
                dataset_id=dataset.id,
                source_type=dataset.source.refresh_strategy if dataset.source else "scheduled_download",
                trigger_type=trigger_type,
                status="queued",
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return job

    def run_refresh(self, refresh_job_id: str, bootstrap: bool = False) -> None:
        settings = get_settings()
        with self._lock:
            with self.session_factory() as session:
                job = session.get(RefreshJob, refresh_job_id)
                if job is None:
                    return

                dataset = session.get(Dataset, job.dataset_id)
                if dataset is None:
                    return

                adapter = get_adapter(dataset.code)
                job.status = "running"
                job.started_at = datetime.now(timezone.utc)
                session.commit()

                try:
                    raw_bytes = adapter.bootstrap_bytes() if bootstrap else adapter.fetch_bytes(settings)
                    checksum = adapter.checksum(raw_bytes)
                    parsed = adapter.parse(raw_bytes, checksum)
                    artifact_path = self._write_artifact(
                        dataset.code,
                        parsed.dataset_version.label,
                        checksum,
                        raw_bytes,
                        adapter.file_extension,
                        settings,
                    )
                    job.rows_read = parsed.dataset_version.row_count

                    latest_version = session.scalar(
                        select(DatasetVersion)
                        .where(DatasetVersion.dataset_id == dataset.id)
                        .order_by(DatasetVersion.published_at.desc())
                    )
                    if latest_version is not None and latest_version.checksum == checksum:
                        job.status = "published"
                        job.rows_written = 0
                        job.error_summary = "Artifact checksum matches latest published version"
                        job.finished_at = datetime.now(timezone.utc)
                        session.commit()
                        logger.info(
                            "refresh-deduplicated source_code=%s dataset_code=%s refresh_job_id=%s version_id=%s",
                            dataset.source.code if dataset.source else "unknown",
                            dataset.code,
                            job.id,
                            latest_version.id,
                        )
                        return

                    version = DatasetVersion(
                        id=str(uuid4()),
                        dataset_id=dataset.id,
                        label=parsed.dataset_version.label,
                        extracted_at=parsed.dataset_version.extracted_at,
                        published_at=parsed.dataset_version.published_at,
                        coverage_start=parsed.dataset_version.coverage_start,
                        coverage_end=parsed.dataset_version.coverage_end,
                        row_count=parsed.dataset_version.row_count,
                        schema_version=parsed.dataset_version.schema_version,
                        checksum=checksum,
                        status="published",
                        lineage={
                            "source_code": dataset.source.code if dataset.source else "",
                            "refresh_job_id": job.id,
                            "artifact_checksum": checksum,
                            **adapter.artifact_metadata(artifact_path, raw_bytes),
                        },
                    )
                    session.add(version)
                    session.flush()

                    self._persist_payload(session, dataset, version, parsed)

                    dataset.latest_version_id = version.id
                    job.status = "published"
                    job.rows_written = parsed.dataset_version.row_count
                    job.finished_at = datetime.now(timezone.utc)
                    job.published_version_id = version.id
                    session.commit()
                    logger.info(
                        "refresh-published source_code=%s dataset_code=%s refresh_job_id=%s version_id=%s",
                        dataset.source.code if dataset.source else "unknown",
                        dataset.code,
                        job.id,
                        version.id,
                    )
                except Exception as exc:
                    session.rollback()
                    failed_job = session.get(RefreshJob, refresh_job_id)
                    if failed_job is not None:
                        failed_job.status = "failed"
                        failed_job.error_summary = str(exc)
                        failed_job.finished_at = datetime.now(timezone.utc)
                        session.commit()
                    logger.exception(
                        "refresh-failed dataset_code=%s refresh_job_id=%s error=%s",
                        dataset.code,
                        refresh_job_id,
                        exc,
                    )
                    return

        self._post_publish(refresh_job_id)

    def bootstrap_missing_versions(self) -> None:
        self.refresh_missing_versions(use_fixtures=True)

    def refresh_missing_versions(self, use_fixtures: bool) -> int:
        with self.session_factory() as session:
            datasets = session.scalars(select(Dataset).where(~Dataset.versions.any()).order_by(Dataset.code)).all()
            dataset_ids = [dataset.id for dataset in datasets if has_adapter(dataset.code)]

        for dataset_id in dataset_ids:
            job = self.queue_refresh(dataset_id, trigger_type="manual")
            self.run_refresh(job.id, bootstrap=use_fixtures)
        return len(dataset_ids)

    def run_due_refreshes(self, force: bool = False) -> int:
        dataset_ids: list[str] = []
        with self.session_factory() as session:
            datasets = session.scalars(select(Dataset).order_by(Dataset.code)).all()
            for dataset in datasets:
                if not has_adapter(dataset.code):
                    continue
                if force or self._is_due(dataset, session):
                    dataset_ids.append(dataset.id)

        runs = 0
        for dataset_id in dataset_ids:
            job = self.queue_refresh(dataset_id, trigger_type="schedule")
            self.run_refresh(job.id)
            runs += 1
        return runs

    def serialize_refresh_job(self, refresh_job: RefreshJob) -> dict[str, str]:
        return {
            "refresh_job_id": refresh_job.id,
            "dataset_id": refresh_job.dataset_id,
            "status": refresh_job.status,
            "requested_at": to_iso8601(refresh_job.created_at) or "",
        }

    def _persist_payload(
        self,
        session: Session,
        dataset: Dataset,
        version: DatasetVersion,
        payload: ParsedDatasetPayload,
    ) -> tuple[dict[str, str], dict[str, str]]:
        source = session.scalar(select(Source).where(Source.id == dataset.source_id))
        if source is None:
            raise ValueError(f"Source {dataset.source_id} not found for dataset {dataset.id}")

        aliases_by_entity_key: dict[str, list[ParsedEntityAlias]] = {}
        for parsed_alias in payload.aliases:
            aliases_by_entity_key.setdefault(parsed_alias.entity_key, []).append(parsed_alias)

        entity_ids_by_key: dict[str, str] = {}
        for parsed_entity in payload.entities:
            validate_entity_type(parsed_entity.entity_type)
            result = harmonization_service.upsert_entity(
                session,
                source=source,
                dataset_version_id=version.id,
                parsed_entity=parsed_entity,
                aliases=aliases_by_entity_key.get(parsed_entity.key, []),
                seen_at=version.published_at,
            )
            entity_ids_by_key[parsed_entity.key] = result.entity.id

        for parsed_alias in payload.aliases:
            entity_id = entity_ids_by_key.get(parsed_alias.entity_key)
            if entity_id is None:
                continue
            self._upsert_alias(session, source.id, entity_id, parsed_alias)

        series_ids_by_key: dict[str, str] = {}
        for parsed_series in payload.metric_series:
            validate_entity_type(parsed_series.entity_type)
            validate_semantic_value_type(parsed_series.semantic_value_type)
            validate_reference_time_kind(parsed_series.reference_time_kind)
            series = self._upsert_series(session, dataset.id, parsed_series)
            series_ids_by_key[parsed_series.key] = series.id

        for parsed_relation in payload.relations:
            validate_relation_type(parsed_relation.relation_type)
            source_entity_id = entity_ids_by_key.get(parsed_relation.source_entity_key)
            target_entity_id = entity_ids_by_key.get(parsed_relation.target_entity_key)
            if source_entity_id is None or target_entity_id is None:
                continue
            relation = session.scalar(
                select(Relation).where(
                    Relation.dataset_version_id == version.id,
                    Relation.relation_type == parsed_relation.relation_type,
                    Relation.source_entity_id == source_entity_id,
                    Relation.target_entity_id == target_entity_id,
                )
            )
            if relation is None:
                relation = Relation(
                    id=str(uuid4()),
                    dataset_version_id=version.id,
                    relation_type=parsed_relation.relation_type,
                    source_entity_id=source_entity_id,
                    target_entity_id=target_entity_id,
                )
                session.add(relation)
            relation.valid_from = parsed_relation.valid_from
            relation.valid_to = parsed_relation.valid_to
            relation.attributes = dict(parsed_relation.attributes)

        for parsed_observation in payload.observations:
            series_id = series_ids_by_key.get(parsed_observation.series_key)
            entity_id = entity_ids_by_key.get(parsed_observation.entity_key)
            if series_id is None or entity_id is None:
                continue
            observation = Observation(
                time=parsed_observation.time,
                series_id=series_id,
                entity_id=entity_id,
                dataset_version_id=version.id,
                value_numeric=parsed_observation.value_numeric,
                value_text=parsed_observation.value_text,
                quality_flag=parsed_observation.quality_flag,
                dimensions=dict(parsed_observation.dimensions),
                published_at=parsed_observation.published_at or version.published_at,
            )
            session.merge(observation)

        for parsed_series in payload.metric_series:
            series_id = series_ids_by_key[parsed_series.key]
            latest_time = session.scalar(
                select(func.max(Observation.time)).where(
                    Observation.series_id == series_id,
                    Observation.dataset_version_id == version.id,
                )
            )
            if latest_time is not None:
                series = session.get(MetricSeries, series_id)
                if series is not None:
                    series.latest_observation_at = latest_time
        semantic_service.persist_payload_semantics(
            session,
            dataset,
            version,
            payload,
            entity_ids_by_key,
            series_ids_by_key,
        )
        return entity_ids_by_key, series_ids_by_key

    def _upsert_alias(
        self,
        session: Session,
        source_id: str,
        entity_id: str,
        parsed_alias: ParsedEntityAlias,
    ) -> None:
        alias = None
        if parsed_alias.external_code:
            alias = session.scalar(
                select(EntityAlias).where(
                    EntityAlias.source_id == source_id,
                    EntityAlias.external_code == parsed_alias.external_code,
                )
            )
        if alias is None:
            alias = session.scalar(
                select(EntityAlias).where(
                    EntityAlias.source_id == source_id,
                    EntityAlias.entity_id == entity_id,
                    EntityAlias.alias_name == parsed_alias.alias_name,
                )
            )
        if alias is None:
            alias = EntityAlias(
                id=str(uuid4()),
                entity_id=entity_id,
                source_id=source_id,
                external_code=parsed_alias.external_code,
                alias_name=parsed_alias.alias_name,
                confidence=parsed_alias.confidence,
            )
            session.add(alias)
            return

        alias.entity_id = entity_id
        alias.alias_name = parsed_alias.alias_name
        alias.external_code = parsed_alias.external_code
        alias.confidence = parsed_alias.confidence

    def _upsert_series(self, session: Session, dataset_id: str, parsed_series: ParsedMetricSeries) -> MetricSeries:
        series = session.scalar(
            select(MetricSeries).where(
                MetricSeries.dataset_id == dataset_id,
                MetricSeries.metric_code == parsed_series.metric_code,
                MetricSeries.entity_type == parsed_series.entity_type,
                MetricSeries.semantic_value_type == parsed_series.semantic_value_type,
                MetricSeries.reference_time_kind == parsed_series.reference_time_kind,
            )
        )
        if series is None:
            series = MetricSeries(
                id=str(uuid4()),
                dataset_id=dataset_id,
                entity_type=parsed_series.entity_type,
                metric_code=parsed_series.metric_code,
                metric_name=parsed_series.metric_name,
                unit=parsed_series.unit,
                temporal_granularity=parsed_series.temporal_granularity,
                semantic_value_type=parsed_series.semantic_value_type,
                reference_time_kind=parsed_series.reference_time_kind,
                dimensions=dict(parsed_series.dimensions),
            )
            session.add(series)
            session.flush()
            return series

        series.metric_name = parsed_series.metric_name
        series.unit = parsed_series.unit
        series.temporal_granularity = parsed_series.temporal_granularity
        series.semantic_value_type = parsed_series.semantic_value_type
        series.reference_time_kind = parsed_series.reference_time_kind
        series.dimensions = dict(parsed_series.dimensions)
        return series

    def _post_publish(self, refresh_job_id: str) -> None:
        with self.session_factory() as session:
            job = session.get(RefreshJob, refresh_job_id)
            if job is None or job.published_version_id is None:
                return
            try:
                evidence_service.rebuild_dataset_version_evidence(session, job.published_version_id)
                get_graph_service().project_dataset_version(session, job.dataset_id, job.published_version_id)
                insight_service.rebuild_overview_snapshot(session)
                session.commit()
            except Exception as exc:
                session.rollback()
                logger.warning(
                    "post-publish-side-effects-failed refresh_job_id=%s error=%s",
                    refresh_job_id,
                    exc,
                )

    def _is_due(self, dataset: Dataset, session: Session) -> bool:
        active_job = session.scalar(
            select(RefreshJob)
            .where(RefreshJob.dataset_id == dataset.id, RefreshJob.status.in_(("queued", "running")))
            .limit(1)
        )
        if active_job is not None:
            return False

        latest_version = session.scalar(
            select(DatasetVersion)
            .where(DatasetVersion.dataset_id == dataset.id)
            .order_by(DatasetVersion.published_at.desc())
        )
        if latest_version is None:
            return True

        now = datetime.now(timezone.utc)
        age = now - latest_version.published_at.astimezone(timezone.utc)
        if dataset.refresh_frequency == "daily":
            return age.total_seconds() >= 86400
        if dataset.refresh_frequency == "monthly":
            return age.total_seconds() >= 86400 * 30
        return False

    def _write_artifact(
        self,
        dataset_code: str,
        label: str,
        checksum: str,
        raw_bytes: bytes,
        file_extension: str,
        settings: Settings,
    ) -> Path:
        safe_label = label.replace(":", "-")
        target_dir = settings.artifacts_path / dataset_code
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{safe_label}__{checksum[:12]}{file_extension}"
        target_path.write_bytes(raw_bytes)
        return target_path
