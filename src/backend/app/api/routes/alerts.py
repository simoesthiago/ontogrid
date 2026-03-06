from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_request_context
from app.schemas.alerts import AlertAckResponse, AlertListResponse, AlertResponse
from app.schemas.auth import RequestContext
from app.services.demo_store import store

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
def list_alerts(
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    asset_id: str | None = None,
    context: RequestContext = Depends(get_request_context),
) -> AlertListResponse:
    items = store.list_alerts(context.tenant_id, status_filter, severity, asset_id)
    return AlertListResponse(items=[AlertResponse(**item) for item in items], total=len(items))


@router.post("/{alert_id}/ack", response_model=AlertAckResponse)
def acknowledge_alert(alert_id: str, context: RequestContext = Depends(get_request_context)) -> AlertAckResponse:
    item = store.acknowledge_alert(context.tenant_id, alert_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return AlertAckResponse(id=item["id"], status=item["status"], acknowledged_at=item["acknowledged_at"])
