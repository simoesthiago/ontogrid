from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean, pstdev
from uuid import uuid4

from app.core.config import settings
from app.schemas.assets import AssetCreate, AssetResponse, MeasurementItem
from app.schemas.cases import CaseCreate
from app.schemas.ingestion import MeasurementRecord


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DemoStore:
    def __init__(self) -> None:
        self.assets: dict[str, dict] = {}
        self.measurements: list[dict] = []
        self.health_history: dict[str, list[dict]] = {}
        self.alerts: dict[str, dict] = {}
        self.cases: dict[str, dict] = {}
        self.jobs: dict[str, dict] = {}
        self._seed()

    def _seed(self) -> None:
        asset = self.create_asset(
            settings.demo_tenant_id,
            AssetCreate(
                external_ref="TR-DEMO-01",
                name="TR-DEMO-01",
                asset_type="transformer",
                substation_name="SE Demo",
                nominal_voltage_kv=230,
                criticality="high",
                status="active",
            ),
        )
        self.ingest_records(
            settings.demo_tenant_id,
            [
                MeasurementRecord(
                    asset_id=asset["id"],
                    measurement_type="temperature",
                    value=78.0,
                    timestamp=utcnow(),
                    quality_flag="good",
                    source="seed",
                )
            ],
        )

    def create_asset(self, tenant_id: str, payload: AssetCreate) -> dict:
        now = utcnow()
        asset_id = str(uuid4())
        item = AssetResponse(
            id=asset_id,
            tenant_id=tenant_id,
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        ).model_dump()
        self.assets[asset_id] = item
        return item

    def list_assets(self, tenant_id: str, q: str | None, asset_type: str | None, status: str | None) -> list[dict]:
        items = [asset for asset in self.assets.values() if asset["tenant_id"] == tenant_id]
        if q:
            items = [asset for asset in items if q.lower() in asset["name"].lower()]
        if asset_type:
            items = [asset for asset in items if asset["asset_type"] == asset_type]
        if status:
            items = [asset for asset in items if asset["status"] == status]
        return items

    def get_asset(self, tenant_id: str, asset_id: str) -> dict | None:
        asset = self.assets.get(asset_id)
        if asset and asset["tenant_id"] == tenant_id:
            return asset
        return None

    def list_measurements(self, tenant_id: str, asset_id: str, measurement_type: str | None, limit: int) -> list[dict]:
        items = [
            measurement
            for measurement in self.measurements
            if measurement["tenant_id"] == tenant_id and measurement["asset_id"] == asset_id
        ]
        if measurement_type:
            items = [measurement for measurement in items if measurement["measurement_type"] == measurement_type]
        items.sort(key=lambda entry: entry["timestamp"], reverse=True)
        return items[:limit]

    def ingest_records(self, tenant_id: str, records: list[MeasurementRecord]) -> tuple[int, int]:
        accepted = 0
        rejected = 0
        for record in records:
            asset = self.get_asset(tenant_id, record.asset_id)
            if asset is None:
                rejected += 1
                continue

            measurement = MeasurementItem(
                timestamp=record.timestamp,
                measurement_type=record.measurement_type,
                value=record.value,
                quality_flag=record.quality_flag,
                source=record.source,
            ).model_dump()
            measurement["tenant_id"] = tenant_id
            measurement["asset_id"] = record.asset_id
            self.measurements.append(measurement)
            accepted += 1
            self.recalculate_asset_health(tenant_id, record.asset_id, record.measurement_type)
        return accepted, rejected

    def recalculate_asset_health(self, tenant_id: str, asset_id: str, measurement_type: str) -> dict:
        recent = self.list_measurements(tenant_id, asset_id, None, 20)
        score = 100.0
        reasons: list[str] = []
        latest_by_type: dict[str, float] = {}
        for item in recent:
            latest_by_type.setdefault(item["measurement_type"], item["value"])

        temperature = latest_by_type.get("temperature")
        vibration = latest_by_type.get("vibration")
        if temperature is not None:
            if temperature > 90:
                score -= 45
                reasons.append("temperature_critical")
            elif temperature > 80:
                score -= 25
                reasons.append("temperature_warning")
        if vibration is not None and vibration > 5:
            score -= 30
            reasons.append("vibration_warning")

        series = [item["value"] for item in recent if item["measurement_type"] == measurement_type]
        if len(series) >= 3:
            current = series[0]
            baseline = mean(series[1:])
            deviation = pstdev(series[1:]) or 0
            if deviation > 0 and abs(current - baseline) / deviation >= 2:
                score -= 15
                reasons.append("zscore_warning")

        score = max(score, 0)
        band = "healthy" if score >= 70 else "warning" if score >= 40 else "critical"
        health = {
            "score": round(score, 2),
            "band": band,
            "calculated_at": utcnow(),
            "inputs": {"reasons": reasons},
        }
        self.health_history.setdefault(asset_id, []).append(health)

        if reasons:
            self.create_alert(
                tenant_id,
                asset_id,
                "critical" if band == "critical" else "high" if band == "warning" else "medium",
                "threshold" if any("temperature" in reason for reason in reasons) else "zscore",
                f"Ativo {asset_id} com sinais: {', '.join(reasons)}",
            )
        return health

    def get_health(self, asset_id: str) -> tuple[dict | None, list[dict]]:
        history = self.health_history.get(asset_id, [])
        current = history[-1] if history else None
        return current, history[-10:]

    def create_alert(self, tenant_id: str, asset_id: str, severity: str, alert_type: str, message: str) -> dict:
        alert_id = str(uuid4())
        alert = {
            "id": alert_id,
            "tenant_id": tenant_id,
            "asset_id": asset_id,
            "severity": severity,
            "status": "open",
            "alert_type": alert_type,
            "message": message,
            "created_at": utcnow(),
            "acknowledged_at": None,
        }
        self.alerts[alert_id] = alert
        return alert

    def list_alerts(self, tenant_id: str, status: str | None, severity: str | None, asset_id: str | None) -> list[dict]:
        items = [alert for alert in self.alerts.values() if alert["tenant_id"] == tenant_id]
        if status:
            items = [alert for alert in items if alert["status"] == status]
        if severity:
            items = [alert for alert in items if alert["severity"] == severity]
        if asset_id:
            items = [alert for alert in items if alert["asset_id"] == asset_id]
        items.sort(key=lambda entry: entry["created_at"], reverse=True)
        return items

    def acknowledge_alert(self, tenant_id: str, alert_id: str) -> dict | None:
        alert = self.alerts.get(alert_id)
        if not alert or alert["tenant_id"] != tenant_id:
            return None
        if alert["status"] != "acknowledged":
            alert["status"] = "acknowledged"
            alert["acknowledged_at"] = utcnow()
        return alert

    def list_cases(self, tenant_id: str) -> list[dict]:
        items = [case for case in self.cases.values() if case["tenant_id"] == tenant_id]
        items.sort(key=lambda entry: entry["created_at"], reverse=True)
        return items

    def create_case(self, tenant_id: str, payload: CaseCreate) -> dict:
        case_id = str(uuid4())
        case = {
            "id": case_id,
            "tenant_id": tenant_id,
            "asset_id": payload.asset_id,
            "alert_id": payload.alert_id,
            "title": payload.title,
            "status": "open",
            "priority": payload.priority,
            "created_at": utcnow(),
        }
        self.cases[case_id] = case
        return case

    def create_job(
        self,
        tenant_id: str,
        source_type: str,
        payload_format: str,
        received: int,
        accepted: int,
        rejected: int,
        error_summary: str | None = None,
    ) -> dict:
        now = utcnow()
        job_id = str(uuid4())
        job = {
            "id": job_id,
            "tenant_id": tenant_id,
            "status": "failed" if error_summary else "completed",
            "source_type": source_type,
            "payload_format": payload_format,
            "records_received": received,
            "records_accepted": accepted,
            "records_rejected": rejected,
            "error_summary": error_summary,
            "created_at": now,
            "completed_at": now,
        }
        self.jobs[job_id] = job
        return job

    def get_job(self, tenant_id: str, job_id: str) -> dict | None:
        job = self.jobs.get(job_id)
        if job and job["tenant_id"] == tenant_id:
            return job
        return None

    def get_neighbors(self, tenant_id: str, asset_id: str) -> dict:
        asset = self.get_asset(tenant_id, asset_id)
        substation_name = asset["substation_name"] if asset else "Unknown"
        substation_id = f"substation-{asset_id}"
        return {
            "asset_id": asset_id,
            "nodes": [
                {"id": asset_id, "type": "Asset", "name": asset["name"] if asset else asset_id},
                {"id": substation_id, "type": "Substation", "name": substation_name},
            ],
            "edges": [{"source": substation_id, "target": asset_id, "type": "CONTAINS"}],
        }

    def get_impact(self, tenant_id: str, asset_id: str) -> dict:
        asset = self.get_asset(tenant_id, asset_id)
        return {
            "asset_id": asset_id,
            "impacted_assets": [
                {"id": asset_id, "name": asset["name"] if asset else asset_id, "reason": "shared_substation"}
            ],
            "impacted_substations": [
                {"id": f"substation-{asset_id}", "name": asset["substation_name"] if asset else "Unknown"}
            ],
        }


store = DemoStore()
