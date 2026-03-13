from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, case, cast, func, literal, select
from sqlalchemy.orm import Session

from app.db.models import Dataset, Entity, MetricSeries, Observation
from app.services.catalog_service import to_iso8601

SUPPORTED_AGGREGATIONS = ["sum", "avg", "count", "min", "max"]


def _title_case(value: str) -> str:
    return " ".join(token.capitalize() for token in value.replace(":", " ").replace("_", " ").split())


def _as_string(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return to_iso8601(value) or ""
    return str(value)


class AnalysisService:
    def get_fields(self, session: Session, dataset_id: str) -> dict[str, object] | None:
        dataset = session.get(Dataset, dataset_id)
        if dataset is None:
            return None

        metric_series = session.scalars(
            select(MetricSeries)
            .where(MetricSeries.dataset_id == dataset_id)
            .order_by(MetricSeries.metric_name, MetricSeries.metric_code)
        ).all()

        if dataset.latest_version_id:
            observation_rows = session.scalars(
                select(Observation).where(Observation.dataset_version_id == dataset.latest_version_id)
            ).all()
        else:
            observation_rows = []

        entity_types = sorted({item.entity_type for item in metric_series if item.entity_type})
        schema_dimensions = [
            str(item)
            for item in list(dataset.schema_summary.get("dimensions", []))
            if item
        ]
        dimension_keys = sorted(
            {
                str(key)
                for row in observation_rows
                for key in dict(row.dimensions or {}).keys()
            }
        )

        entity_label = "Entidade"
        if entity_types:
            primary_entity_type = entity_types[0]
            entity_label = _title_case(primary_entity_type)
            for item in schema_dimensions:
                if item == primary_entity_type:
                    entity_label = _title_case(item)
                    break

        dimensions: list[dict[str, object]] = []
        if metric_series:
            dimensions.append({"id": "entity_name", "label": entity_label, "kind": "entity"})
        if observation_rows:
            dimensions.append({"id": "timestamp", "label": "Timestamp", "kind": "time"})
        for key in dimension_keys:
            dimensions.append({"id": f"dim:{key}", "label": _title_case(key), "kind": "dimension"})

        metric_fields: list[dict[str, object]] = []
        seen_metric_codes: set[str] = set()
        for item in metric_series:
            if item.metric_code in seen_metric_codes:
                continue
            seen_metric_codes.add(item.metric_code)
            metric_fields.append(
                {
                    "field": item.metric_code,
                    "label": item.metric_name,
                    "unit": item.unit,
                    "supported_aggregations": SUPPORTED_AGGREGATIONS,
                }
            )

        return {
            "dataset_id": dataset_id,
            "dimensions": dimensions,
            "metrics": metric_fields,
            "time_fields": ["timestamp"] if observation_rows else [],
            "entity_field": "entity_name" if metric_series else None,
            "default_measure": metric_fields[0]["field"] if metric_fields else None,
        }

    def run_query(self, session: Session, config: dict[str, object]) -> dict[str, object]:
        dataset_id = str(config["dataset_id"])
        dataset = session.get(Dataset, dataset_id)
        if dataset is None:
            raise ValueError("Dataset not found")
        if dataset.latest_version_id is None:
            return {
                "dataset_id": dataset_id,
                "columns": [],
                "rows": [],
                "totals": {},
                "applied_filters": list(config.get("filters", [])),
            }

        rows_config = [str(item) for item in list(config.get("rows", []))]
        columns_config = [str(item) for item in list(config.get("columns", []))]
        measure_configs = [
            {
                "field": str(item["field"]),
                "aggregation": str(item["aggregation"]),
            }
            for item in list(config.get("measures", []))
            if isinstance(item, dict) and item.get("field") and item.get("aggregation")
        ]
        if not measure_configs:
            raise ValueError("At least one measure is required")
        filters = [
            {
                "field": str(item["field"]),
                "operator": str(item["operator"]),
                "values": [str(value) for value in list(item.get("values", []))],
            }
            for item in list(config.get("filters", []))
            if isinstance(item, dict) and item.get("field") and item.get("operator")
        ]
        entity_id = config.get("entity_id")

        dimension_ids = []
        for item in rows_config + columns_config:
            if item not in dimension_ids:
                dimension_ids.append(item)

        base_query = (
            select()
            .select_from(Observation)
            .join(MetricSeries, MetricSeries.id == Observation.series_id)
            .join(Entity, Entity.id == Observation.entity_id)
            .where(
                MetricSeries.dataset_id == dataset_id,
                Observation.dataset_version_id == dataset.latest_version_id,
            )
        )

        if entity_id:
            base_query = base_query.where(Observation.entity_id == str(entity_id))

        dimension_selects: list[tuple[str, str, object]] = []
        dimension_group_bys: list[object] = []
        for field_id in dimension_ids:
            label, expression = self._field_expression(field_id)
            named_expression = expression.label(field_id)
            dimension_selects.append((field_id, label, named_expression))
            dimension_group_bys.append(expression)

        metric_codes = [item["field"] for item in measure_configs]
        if metric_codes:
            base_query = base_query.where(MetricSeries.metric_code.in_(metric_codes))

        for filter_item in filters:
            label, expression = self._field_expression(filter_item["field"])
            del label
            if filter_item["operator"] != "in":
                raise ValueError("Unsupported filter operator")
            if filter_item["field"] == "timestamp":
                values = [datetime.fromisoformat(value.replace("Z", "+00:00")) for value in filter_item["values"]]
            else:
                values = filter_item["values"]
            base_query = base_query.where(expression.in_(values))

        measure_selects: list[tuple[str, object]] = []
        for measure in measure_configs:
            metric_value_expr = case(
                (MetricSeries.metric_code == measure["field"], Observation.value_numeric),
                else_=None,
            )
            count_expr = case(
                (MetricSeries.metric_code == measure["field"], literal(1)),
                else_=None,
            )
            measure_key = f"{measure['field']}__{measure['aggregation']}"
            if measure["aggregation"] == "sum":
                expression = func.sum(metric_value_expr)
            elif measure["aggregation"] == "avg":
                expression = func.avg(metric_value_expr)
            elif measure["aggregation"] == "min":
                expression = func.min(metric_value_expr)
            elif measure["aggregation"] == "max":
                expression = func.max(metric_value_expr)
            elif measure["aggregation"] == "count":
                expression = func.count(count_expr)
            else:
                raise ValueError("Unsupported aggregation")
            measure_selects.append((measure_key, expression.label(measure_key)))

        selected_columns = [item[2] for item in dimension_selects] + [item[1] for item in measure_selects]
        query = base_query.with_only_columns(*selected_columns)
        if dimension_group_bys:
            query = query.group_by(*dimension_group_bys).order_by(*dimension_group_bys)

        result_rows = session.execute(query.limit(500)).all()

        columns = [
            {"id": field_id, "label": label, "kind": "dimension"}
            for field_id, label, _ in dimension_selects
        ] + [
            {"id": key, "label": _title_case(key), "kind": "measure"}
            for key, _ in measure_selects
        ]

        payload_rows: list[dict[str, object]] = []
        totals: dict[str, float | int | None] = {key: 0 for key, _ in measure_selects}
        for result in result_rows:
            values: dict[str, object | None] = {}
            for field_id, _, _ in dimension_selects:
                values[field_id] = _as_string(getattr(result, field_id))
            for measure_key, _ in measure_selects:
                measure_value = getattr(result, measure_key)
                values[measure_key] = measure_value
                if measure_value is not None:
                    totals[measure_key] = (totals.get(measure_key) or 0) + measure_value
            payload_rows.append({"values": values})

        if not measure_selects:
            totals = {}

        return {
            "dataset_id": dataset_id,
            "columns": columns,
            "rows": payload_rows,
            "totals": totals,
            "applied_filters": filters,
        }

    def _field_expression(self, field_id: str) -> tuple[str, object]:
        if field_id == "entity_name":
            return "Entidade", Entity.name
        if field_id == "timestamp":
            return "Timestamp", cast(Observation.time, DateTime(timezone=True))
        if field_id.startswith("dim:"):
            key = field_id.split(":", 1)[1]
            return _title_case(key), Observation.dimensions[key].as_string()
        raise ValueError(f"Unsupported field: {field_id}")


analysis_service = AnalysisService()
