from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from uuid import uuid4

from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session, joinedload

from app.copilot.cache import get_copilot_cache
from app.copilot.client import LlmProviderUnavailable, LlmRequestFailed, get_llm_client
from app.core.config import get_settings
from app.db.models import CopilotTrace, Dataset, DatasetVersion, Entity, EvidenceRegistry, MetricSeries, Observation, Source
from app.schemas.copilot import CopilotQueryRequest
from app.services.catalog_service import to_iso8601
from app.services.evidence_service import evidence_service
from app.services.graph_service import GraphBackendUnavailable, get_graph_service


class CopilotProviderUnavailable(RuntimeError):
    pass


@dataclass
class ResolvedScope:
    datasets: list[Dataset]
    versions: list[DatasetVersion]
    entity_ids: list[str]
    start: datetime | None
    end: datetime | None
    locale: str


class CopilotService:
    def query(self, session: Session, payload: CopilotQueryRequest) -> dict[str, object]:
        settings = get_settings()
        if not settings.llm_enabled:
            raise CopilotProviderUnavailable("LLM provider is not configured")

        scope = self._resolve_scope(session, payload)
        grounding = self._build_grounding(session, scope)
        cache_key = self._cache_key(payload.question, scope, grounding["dataset_version_ids"])
        cached = get_copilot_cache().get_json(cache_key)
        if cached is not None:
            response = dict(cached)
            response["cached"] = True
            self._persist_trace(session, payload.question, scope, response)
            session.commit()
            response.pop("cached", None)
            return response

        if not grounding["dataset_version_ids"] or (
            not grounding["observations"] and not grounding["evidence_claims"]
        ):
            response = {
                "answer": "Nao encontrei grounding suficiente nas versoes publicadas atuais para responder com seguranca.",
                "citations": [],
                "follow_up_questions": [
                    "Quais datasets devo priorizar?",
                    "Quero restringir a resposta a um submercado ou fonte.",
                ],
            }
            self._persist_trace(session, payload.question, scope, response)
            session.commit()
            return response

        try:
            llm_payload = get_llm_client().complete_json(
                system_prompt=self._system_prompt(),
                user_prompt=self._user_prompt(payload.question, scope, grounding),
            )
        except (LlmProviderUnavailable, LlmRequestFailed) as exc:
            raise CopilotProviderUnavailable(str(exc)) from exc

        response = {
            "answer": str(llm_payload.get("answer", "")).strip()
            or "Nao foi possivel gerar uma resposta grounded no momento.",
            "citations": grounding["citations"],
            "follow_up_questions": self._normalize_follow_ups(llm_payload.get("follow_up_questions")),
        }
        get_copilot_cache().set_json(cache_key, response, settings.copilot_cache_ttl_seconds)
        self._persist_trace(session, payload.question, scope, response)
        session.commit()
        return response

    def _resolve_scope(self, session: Session, payload: CopilotQueryRequest) -> ResolvedScope:
        start = self._parse_timestamp(payload.start)
        end = self._parse_timestamp(payload.end)

        dataset_query: Select[tuple[Dataset]] = (
            select(Dataset)
            .options(joinedload(Dataset.source), joinedload(Dataset.latest_version))
            .order_by(Dataset.code)
        )
        if payload.dataset_ids:
            dataset_query = dataset_query.where(Dataset.id.in_(payload.dataset_ids))
        else:
            dataset_query = dataset_query.where(Dataset.latest_version_id.is_not(None))
        datasets = session.scalars(dataset_query).unique().all()
        versions = [dataset.latest_version for dataset in datasets if dataset.latest_version is not None]

        entity_ids = list(payload.entity_ids)
        if not entity_ids and versions:
            entity_ids = session.scalars(
                select(Entity.id)
                .join(Observation, Observation.entity_id == Entity.id)
                .where(Observation.dataset_version_id.in_([version.id for version in versions]))
                .distinct()
                .limit(5)
            ).all()

        return ResolvedScope(
            datasets=datasets,
            versions=versions,
            entity_ids=entity_ids,
            start=start,
            end=end,
            locale=payload.locale,
        )

    def _build_grounding(self, session: Session, scope: ResolvedScope) -> dict[str, object]:
        version_ids = [version.id for version in scope.versions]
        if not version_ids:
            return {
                "dataset_version_ids": [],
                "datasets": [],
                "observations": [],
                "evidence_claims": [],
                "graph_context": [],
                "citations": [],
            }

        observation_query = (
            select(
                Source.code.label("source_code"),
                Dataset.id.label("dataset_id"),
                Dataset.code.label("dataset_code"),
                Dataset.name.label("dataset_name"),
                DatasetVersion.id.label("version_id"),
                DatasetVersion.label.label("version_label"),
                MetricSeries.id.label("series_id"),
                MetricSeries.metric_code.label("metric_code"),
                MetricSeries.metric_name.label("metric_name"),
                MetricSeries.unit.label("unit"),
                Entity.id.label("entity_id"),
                Entity.name.label("entity_name"),
                Observation.time.label("time"),
                Observation.value_numeric.label("value_numeric"),
                Observation.value_text.label("value_text"),
            )
            .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
            .join(Source, Source.id == Dataset.source_id)
            .join(MetricSeries, MetricSeries.dataset_id == Dataset.id)
            .join(
                Observation,
                and_(
                    Observation.series_id == MetricSeries.id,
                    Observation.dataset_version_id == DatasetVersion.id,
                ),
            )
            .join(Entity, Entity.id == Observation.entity_id)
            .where(DatasetVersion.id.in_(version_ids))
            .order_by(Dataset.code, Observation.time.desc())
        )
        if scope.entity_ids:
            observation_query = observation_query.where(Observation.entity_id.in_(scope.entity_ids))
        if scope.start is not None:
            observation_query = observation_query.where(Observation.time >= scope.start)
        if scope.end is not None:
            observation_query = observation_query.where(Observation.time <= scope.end)

        observations = [
            {
                "source_code": row.source_code,
                "dataset_id": row.dataset_id,
                "dataset_code": row.dataset_code,
                "dataset_name": row.dataset_name,
                "version_id": row.version_id,
                "version_label": row.version_label,
                "series_id": row.series_id,
                "metric_code": row.metric_code,
                "metric_name": row.metric_name,
                "unit": row.unit,
                "entity_id": row.entity_id,
                "entity_name": row.entity_name,
                "timestamp": to_iso8601(row.time),
                "value": row.value_numeric if row.value_numeric is not None else row.value_text,
            }
            for row in session.execute(observation_query.limit(100)).all()
        ]

        evidence_keys = [
            evidence_service.observation_scope_id(item["series_id"], item["entity_id"], item["timestamp"] or "")
            for item in observations
            if item["timestamp"]
        ]
        evidence_rows = session.execute(
            select(EvidenceRegistry.scope_id, EvidenceRegistry.id)
            .where(
                EvidenceRegistry.dataset_version_id.in_(version_ids),
                EvidenceRegistry.scope_id.in_(evidence_keys),
            )
        ).all() if evidence_keys else []
        evidence_by_scope_id = {scope_id: evidence_id for scope_id, evidence_id in evidence_rows}

        for item in observations:
            timestamp = item["timestamp"] or ""
            scope_id = evidence_service.observation_scope_id(item["series_id"], item["entity_id"], timestamp)
            item["evidence_id"] = evidence_by_scope_id.get(scope_id)

        evidence_query = (
            select(
                Source.code.label("source_code"),
                Dataset.id.label("dataset_id"),
                Dataset.code.label("dataset_code"),
                DatasetVersion.id.label("version_id"),
                EvidenceRegistry.id.label("evidence_id"),
                EvidenceRegistry.entity_id.label("entity_id"),
                EvidenceRegistry.scope_type.label("scope_type"),
                EvidenceRegistry.scope_id.label("scope_id"),
                EvidenceRegistry.claim_text.label("claim_text"),
            )
            .join(DatasetVersion, DatasetVersion.id == EvidenceRegistry.dataset_version_id)
            .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
            .join(Source, Source.id == Dataset.source_id)
            .where(EvidenceRegistry.dataset_version_id.in_(version_ids))
            .order_by(EvidenceRegistry.created_at.desc())
        )
        if scope.entity_ids:
            evidence_query = evidence_query.where(EvidenceRegistry.entity_id.in_(scope.entity_ids))
        if scope.start is not None:
            evidence_query = evidence_query.where(DatasetVersion.published_at >= scope.start)
        if scope.end is not None:
            evidence_query = evidence_query.where(DatasetVersion.published_at <= scope.end)
        evidence_claims = [
            {
                "source_code": row.source_code,
                "dataset_id": row.dataset_id,
                "dataset_code": row.dataset_code,
                "version_id": row.version_id,
                "evidence_id": row.evidence_id,
                "entity_id": row.entity_id,
                "scope_type": row.scope_type,
                "scope_id": row.scope_id,
                "claim_text": row.claim_text,
            }
            for row in session.execute(evidence_query.limit(60)).all()
        ]

        datasets = [
            {
                "dataset_id": dataset.id,
                "dataset_code": dataset.code,
                "dataset_name": dataset.name,
                "source_code": dataset.source.code if dataset.source else "",
                "description": dataset.description,
                "schema_summary": dataset.schema_summary,
                "latest_version_id": dataset.latest_version.id if dataset.latest_version else "",
                "latest_version_label": dataset.latest_version.label if dataset.latest_version else "",
            }
            for dataset in scope.datasets
        ]

        graph_context = []
        for entity_id in scope.entity_ids[:3]:
            try:
                neighbors = get_graph_service().get_neighbors(session, entity_id)
            except GraphBackendUnavailable:
                neighbors = None
            if neighbors is not None:
                graph_context.append(neighbors)

        citations: list[dict[str, object]] = []
        seen: set[tuple[str, str, str, str | None]] = set()
        for item in observations:
            key = (
                item["source_code"],
                item["dataset_id"],
                item["version_id"],
                item["entity_id"],
                item.get("evidence_id"),
            )
            if key in seen:
                continue
            seen.add(key)
            citations.append(
                {
                    "source_code": item["source_code"],
                    "dataset_id": item["dataset_id"],
                    "version_id": item["version_id"],
                    "entity_id": item["entity_id"],
                    "evidence_id": item.get("evidence_id"),
                }
            )

        for claim in evidence_claims:
            key = (
                claim["source_code"],
                claim["dataset_id"],
                claim["version_id"],
                claim["entity_id"],
                claim["evidence_id"],
            )
            if key in seen:
                continue
            seen.add(key)
            citations.append(
                {
                    "source_code": claim["source_code"],
                    "dataset_id": claim["dataset_id"],
                    "version_id": claim["version_id"],
                    "entity_id": claim["entity_id"],
                    "evidence_id": claim["evidence_id"],
                }
            )

        return {
            "dataset_version_ids": version_ids,
            "datasets": datasets,
            "observations": observations,
            "evidence_claims": evidence_claims,
            "graph_context": graph_context,
            "citations": citations,
        }

    def _persist_trace(
        self,
        session: Session,
        question: str,
        scope: ResolvedScope,
        response: dict[str, object],
    ) -> None:
        session.add(
            CopilotTrace(
                id=str(uuid4()),
                question=question,
                scope={
                    "dataset_ids": [dataset.id for dataset in scope.datasets],
                    "dataset_version_ids": [version.id for version in scope.versions],
                    "entity_ids": scope.entity_ids,
                    "start": to_iso8601(scope.start),
                    "end": to_iso8601(scope.end),
                    "locale": scope.locale,
                },
                answer_payload=response,
            )
        )

    def _cache_key(self, question: str, scope: ResolvedScope, dataset_version_ids: list[str]) -> str:
        normalized_question = re.sub(r"\s+", " ", question.strip().lower())
        payload = json.dumps(
            {
                "question": normalized_question,
                "dataset_ids": [dataset.id for dataset in scope.datasets],
                "dataset_version_ids": sorted(dataset_version_ids),
                "entity_ids": sorted(scope.entity_ids),
                "start": to_iso8601(scope.start),
                "end": to_iso8601(scope.end),
                "locale": scope.locale,
            },
            sort_keys=True,
            ensure_ascii=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _system_prompt(self) -> str:
        return (
            "Voce e o copilot analitico do OntoGrid. Responda apenas com base no contexto fornecido. "
            "Nao invente fatos nem citacoes. Responda em JSON com as chaves "
            '"answer" e "follow_up_questions".'
        )

    def _user_prompt(self, question: str, scope: ResolvedScope, grounding: dict[str, object]) -> str:
        return json.dumps(
            {
                "question": question,
                "locale": scope.locale,
                "time_window": {
                    "start": to_iso8601(scope.start),
                    "end": to_iso8601(scope.end),
                },
                "datasets": grounding["datasets"],
                "observations": grounding["observations"],
                "evidence_claims": grounding["evidence_claims"],
                "graph_context": grounding["graph_context"],
            },
            ensure_ascii=True,
        )

    def _normalize_follow_ups(self, payload: object) -> list[str]:
        if not isinstance(payload, list):
            return []
        return [str(item).strip() for item in payload if str(item).strip()][:3]

    def _parse_timestamp(self, value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


@lru_cache
def get_copilot_service() -> CopilotService:
    return CopilotService()


copilot_service = get_copilot_service()
