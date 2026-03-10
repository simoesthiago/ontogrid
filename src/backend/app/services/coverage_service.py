from __future__ import annotations

from collections import defaultdict

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.catalog_inventory import SOURCE_DEFINITIONS
from app.db.models import Dataset
from app.ingestion.registry import has_adapter


class CoverageService:
    def get_catalog_coverage(self, session: Session) -> dict[str, object]:
        query: Select[tuple[Dataset]] = (
            select(Dataset)
            .options(joinedload(Dataset.source), joinedload(Dataset.latest_version))
            .order_by(Dataset.source_id, Dataset.domain, Dataset.name)
        )
        datasets = session.scalars(query).unique().all()

        source_documents = {
            source.code: str(source.doc_path.relative_to(source.doc_path.parents[2])).replace("\\", "/")
            for source in SOURCE_DEFINITIONS
        }
        source_names = {source.code: source.name for source in SOURCE_DEFINITIONS}
        source_order = {source.code: index for index, source in enumerate(SOURCE_DEFINITIONS)}

        totals = {
            "inventoried_total": 0,
            "documented_only_total": 0,
            "adapter_enabled_total": 0,
            "published_total": 0,
        }
        source_stats: dict[str, dict[str, object]] = {}
        family_stats: dict[tuple[str, str], dict[str, object]] = defaultdict(
            lambda: {
                "inventoried_total": 0,
                "documented_only_total": 0,
                "adapter_enabled_total": 0,
                "published_total": 0,
            }
        )

        for dataset in datasets:
            if dataset.source is None:
                continue

            source_code = dataset.source.code
            source_entry = source_stats.setdefault(
                source_code,
                {
                    "source_code": source_code,
                    "source_name": source_names.get(source_code, dataset.source.name),
                    "source_document": source_documents.get(source_code, ""),
                    "inventoried_total": 0,
                    "documented_only_total": 0,
                    "adapter_enabled_total": 0,
                    "published_total": 0,
                },
            )

            status = self._ingestion_status(dataset)
            source_entry["inventoried_total"] += 1
            totals["inventoried_total"] += 1
            family_entry = family_stats[(source_code, dataset.domain)]
            family_entry["inventoried_total"] += 1

            if status == "published":
                source_entry["published_total"] += 1
                totals["published_total"] += 1
                family_entry["published_total"] += 1
            elif status == "adapter_enabled":
                source_entry["adapter_enabled_total"] += 1
                totals["adapter_enabled_total"] += 1
                family_entry["adapter_enabled_total"] += 1
            else:
                source_entry["documented_only_total"] += 1
                totals["documented_only_total"] += 1
                family_entry["documented_only_total"] += 1

        sources = sorted(source_stats.values(), key=lambda item: source_order.get(str(item["source_code"]), 999))
        families = [
            {
                "source_code": source_code,
                "family": family,
                **stats,
            }
            for (source_code, family), stats in family_stats.items()
        ]
        families.sort(key=lambda item: (source_order.get(str(item["source_code"]), 999), str(item["family"])))

        return {
            **totals,
            "sources": sources,
            "families": families,
        }

    def _ingestion_status(self, dataset: Dataset) -> str:
        if dataset.latest_version is not None:
            return "published"
        if has_adapter(dataset.code):
            return "adapter_enabled"
        return "documented_only"


coverage_service = CoverageService()
