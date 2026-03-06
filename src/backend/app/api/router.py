from fastapi import APIRouter

from app.api.routes import alerts, assets, auth, cases, graph, ingestion


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(assets.router)
api_router.include_router(alerts.router)
api_router.include_router(cases.router)
api_router.include_router(ingestion.router)
api_router.include_router(graph.router)
