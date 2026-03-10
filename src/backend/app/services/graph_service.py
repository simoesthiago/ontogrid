from __future__ import annotations

import json
import logging
import re
from functools import lru_cache

from neo4j import GraphDatabase
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.config import get_settings
from app.db.models import Dataset, Entity, Observation, Relation

logger = logging.getLogger(__name__)


class GraphBackendUnavailable(RuntimeError):
    pass


class GraphService:
    def __init__(self) -> None:
        self._driver = None

    def list_entities(
        self,
        session: Session,
        *,
        q: str | None,
        entity_type: str | None,
        source: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        del session
        params = {
            "entity_type": entity_type,
            "source": source,
            "term": q.lower() if q else None,
            "limit": limit,
            "offset": offset,
        }
        total_rows = self._run_query(
            """
            MATCH (entity:Entity)
            OPTIONAL MATCH (entity)<-[:REFERENCES]-(:Dataset)-[:PUBLISHED_BY]->(source:Source)
            WITH entity, collect(DISTINCT source.code) AS source_codes
            WHERE ($entity_type IS NULL OR entity.entity_type = $entity_type)
              AND ($source IS NULL OR $source IN source_codes)
              AND (
                    $term IS NULL
                    OR toLower(entity.name) CONTAINS $term
                    OR toLower(coalesce(entity.canonical_code, "")) CONTAINS $term
                    OR any(alias IN coalesce(entity.aliases, []) WHERE toLower(alias) CONTAINS $term)
                  )
            RETURN count(DISTINCT entity) AS total
            """,
            params,
        )
        entity_rows = self._run_query(
            """
            MATCH (entity:Entity)
            OPTIONAL MATCH (entity)<-[:REFERENCES]-(:Dataset)-[:PUBLISHED_BY]->(source:Source)
            WITH entity, collect(DISTINCT source.code) AS source_codes
            WHERE ($entity_type IS NULL OR entity.entity_type = $entity_type)
              AND ($source IS NULL OR $source IN source_codes)
              AND (
                    $term IS NULL
                    OR toLower(entity.name) CONTAINS $term
                    OR toLower(coalesce(entity.canonical_code, "")) CONTAINS $term
                    OR any(alias IN coalesce(entity.aliases, []) WHERE toLower(alias) CONTAINS $term)
                  )
            RETURN entity
            ORDER BY entity.entity_type, entity.name
            SKIP $offset
            LIMIT $limit
            """,
            params,
        )
        total = int(total_rows[0]["total"]) if total_rows else 0
        return [self._serialize_entity_node(record["entity"]) for record in entity_rows], total

    def get_entity(self, session: Session, entity_id: str) -> dict[str, object] | None:
        del session
        rows = self._run_query(
            """
            MATCH (entity:Entity {id: $entity_id})
            RETURN entity
            LIMIT 1
            """,
            {"entity_id": entity_id},
        )
        if not rows:
            return None
        entity = rows[0]["entity"]
        return {
            "id": entity["id"],
            "entity_type": entity.get("entity_type", ""),
            "canonical_code": entity.get("canonical_code", "") or "",
            "name": entity.get("name", ""),
            "attributes": self._deserialize_attributes(entity.get("attributes_json")),
        }

    def get_neighbors(self, session: Session, entity_id: str) -> dict[str, object] | None:
        del session
        entity_rows = self._run_query(
            """
            MATCH (entity:Entity {id: $entity_id})
            RETURN entity
            LIMIT 1
            """,
            {"entity_id": entity_id},
        )
        if not entity_rows:
            return None

        entity = entity_rows[0]["entity"]
        nodes: dict[str, dict[str, str]] = {
            entity["id"]: {"id": entity["id"], "type": "Entity", "name": entity.get("name", "")}
        }
        edges: dict[tuple[str, str, str], dict[str, str]] = {}
        provenance_ids: set[str] = set()

        dataset_rows = self._run_query(
            """
            MATCH (dataset:Dataset)-[ref:REFERENCES]->(entity:Entity {id: $entity_id})
            RETURN dataset, ref
            """,
            {"entity_id": entity_id},
        )
        for record in dataset_rows:
            dataset = record["dataset"]
            ref = record["ref"]
            dataset_id = dataset["id"]
            nodes[dataset_id] = {"id": dataset_id, "type": "Dataset", "name": dataset.get("name", "")}
            edges[(dataset_id, entity_id, "REFERENCES")] = {
                "source": dataset_id,
                "target": entity_id,
                "type": "REFERENCES",
            }
            if ref.get("dataset_version_id"):
                provenance_ids.add(ref["dataset_version_id"])

        relation_rows = self._run_query(
            """
            MATCH (entity:Entity {id: $entity_id})-[rel]-(neighbor:Entity)
            WHERE type(rel) <> 'REFERENCES'
            RETURN startNode(rel) AS source_node, endNode(rel) AS target_node, rel
            """,
            {"entity_id": entity_id},
        )
        for record in relation_rows:
            source_node = record["source_node"]
            target_node = record["target_node"]
            relation = record["rel"]
            edge_type = relation.type
            nodes.setdefault(
                source_node["id"],
                {"id": source_node["id"], "type": "Entity", "name": source_node.get("name", "")},
            )
            nodes.setdefault(
                target_node["id"],
                {"id": target_node["id"], "type": "Entity", "name": target_node.get("name", "")},
            )
            edges[(source_node["id"], target_node["id"], edge_type)] = {
                "source": source_node["id"],
                "target": target_node["id"],
                "type": edge_type,
            }
            if relation.get("dataset_version_id"):
                provenance_ids.add(relation["dataset_version_id"])

        return {
            "entity_id": entity_id,
            "nodes": list(nodes.values()),
            "edges": list(edges.values()),
            "provenance": {"dataset_version_ids": sorted(provenance_ids)},
        }

    def project_dataset_version(self, session: Session, dataset_id: str, dataset_version_id: str) -> None:
        driver = self._get_driver(required=False)
        if driver is None:
            return

        dataset = session.scalar(
            select(Dataset)
            .options(joinedload(Dataset.source))
            .where(Dataset.id == dataset_id)
        )
        if dataset is None or dataset.source is None:
            return

        entity_ids = set(
            session.scalars(
                select(Observation.entity_id).where(Observation.dataset_version_id == dataset_version_id)
            ).all()
        )
        relation_rows = session.scalars(
            select(Relation).where(Relation.dataset_version_id == dataset_version_id)
        ).all()
        for relation in relation_rows:
            entity_ids.add(relation.source_entity_id)
            entity_ids.add(relation.target_entity_id)

        entities = []
        if entity_ids:
            entities = session.scalars(
                select(Entity)
                .where(Entity.id.in_(entity_ids))
                .options(selectinload(Entity.aliases))
            ).all()

        try:
            with driver.session() as neo4j_session:
                neo4j_session.run(
                    """
                    MERGE (source:Source {id: $source_id})
                    SET source.code = $source_code,
                        source.name = $source_name,
                        source.type = "Source"
                    """,
                    source_id=dataset.source.id,
                    source_code=dataset.source.code,
                    source_name=dataset.source.name,
                )
                neo4j_session.run(
                    """
                    MERGE (dataset:Dataset {id: $dataset_id})
                    SET dataset.code = $dataset_code,
                        dataset.name = $dataset_name,
                        dataset.type = "Dataset",
                        dataset.source_code = $source_code,
                        dataset.dataset_version_id = $dataset_version_id
                    """,
                    dataset_id=dataset.id,
                    dataset_code=dataset.code,
                    dataset_name=dataset.name,
                    source_code=dataset.source.code,
                    dataset_version_id=dataset_version_id,
                )
                neo4j_session.run(
                    """
                    MATCH (dataset:Dataset {id: $dataset_id})
                    MATCH (source:Source {id: $source_id})
                    MERGE (dataset)-[:PUBLISHED_BY]->(source)
                    """,
                    dataset_id=dataset.id,
                    source_id=dataset.source.id,
                )
                neo4j_session.run(
                    """
                    MATCH (dataset:Dataset {id: $dataset_id})-[ref:REFERENCES]->(:Entity)
                    DELETE ref
                    """,
                    dataset_id=dataset.id,
                )
                neo4j_session.run(
                    """
                    MATCH (:Entity)-[rel]->(:Entity)
                    WHERE rel.dataset_id = $dataset_id
                    DELETE rel
                    """,
                    dataset_id=dataset.id,
                )

                for entity in entities:
                    aliases = sorted({alias.alias_name for alias in entity.aliases})
                    neo4j_session.run(
                        """
                        MERGE (entity:Entity {id: $entity_id})
                        SET entity.type = "Entity",
                            entity.entity_type = $entity_type,
                            entity.name = $name,
                            entity.canonical_code = $canonical_code,
                            entity.jurisdiction = $jurisdiction,
                            entity.aliases = $aliases,
                            entity.attributes_json = $attributes_json,
                            entity.dataset_version_id = $dataset_version_id
                        """,
                        entity_id=entity.id,
                        entity_type=entity.entity_type,
                        name=entity.name,
                        canonical_code=entity.canonical_code,
                        jurisdiction=entity.jurisdiction,
                        aliases=aliases,
                        attributes_json=json.dumps(entity.attributes, ensure_ascii=True),
                        dataset_version_id=dataset_version_id,
                    )
                    neo4j_session.run(
                        """
                        MATCH (dataset:Dataset {id: $dataset_id})
                        MATCH (entity:Entity {id: $entity_id})
                        MERGE (dataset)-[rel:REFERENCES]->(entity)
                        SET rel.dataset_id = $dataset_id,
                            rel.dataset_version_id = $dataset_version_id
                        """,
                        dataset_id=dataset.id,
                        entity_id=entity.id,
                        dataset_version_id=dataset_version_id,
                    )

                for relation in relation_rows:
                    rel_type = self._sanitize_relation_type(relation.relation_type)
                    neo4j_session.run(
                        f"""
                        MATCH (source:Entity {{id: $source_entity_id}})
                        MATCH (target:Entity {{id: $target_entity_id}})
                        MERGE (source)-[rel:{rel_type} {{dataset_id: $dataset_id}}]->(target)
                        SET rel.dataset_version_id = $dataset_version_id
                        """,
                        source_entity_id=relation.source_entity_id,
                        target_entity_id=relation.target_entity_id,
                        dataset_id=dataset.id,
                        dataset_version_id=dataset_version_id,
                    )
        except Exception as exc:  # pragma: no cover - depends on external Neo4j availability
            logger.warning(
                "neo4j-projection-failed dataset_id=%s dataset_version_id=%s error=%s",
                dataset_id,
                dataset_version_id,
                exc,
            )

    def _get_driver(self, required: bool) -> object | None:
        settings = get_settings()
        if not settings.neo4j_enabled:
            if required:
                raise GraphBackendUnavailable("Neo4j is not configured for graph queries")
            return None
        if self._driver is None:  # pragma: no branch - simple lazy init
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
            )
        return self._driver

    def _run_query(self, statement: str, parameters: dict[str, object]) -> list[object]:
        driver = self._get_driver(required=True)
        try:
            with driver.session() as neo4j_session:
                return list(neo4j_session.run(statement, **parameters))
        except GraphBackendUnavailable:
            raise
        except Exception as exc:  # pragma: no cover - depends on external Neo4j availability
            raise GraphBackendUnavailable("Neo4j is unavailable for graph queries") from exc

    def _serialize_entity_node(self, entity: object) -> dict[str, object]:
        return {
            "id": entity["id"],
            "entity_type": entity.get("entity_type", ""),
            "canonical_code": entity.get("canonical_code", "") or "",
            "name": entity.get("name", ""),
            "aliases": sorted(str(alias) for alias in entity.get("aliases", [])),
            "jurisdiction": entity.get("jurisdiction", ""),
        }

    def _deserialize_attributes(self, payload: object) -> dict[str, object]:
        if not payload:
            return {}
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, str):
            try:
                parsed = json.loads(payload)
            except json.JSONDecodeError:
                return {}
            if isinstance(parsed, dict):
                return parsed
        return {}

    def _sanitize_relation_type(self, value: str) -> str:
        cleaned = re.sub(r"[^A-Z0-9_]", "_", value.upper())
        return cleaned or "RELATES_TO"


@lru_cache
def get_graph_service() -> GraphService:
    return GraphService()
