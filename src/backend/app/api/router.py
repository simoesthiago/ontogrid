from fastapi import APIRouter

from app.api.routes import copilot, datasets, graph, insights, series, sources


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(sources.router)
api_router.include_router(datasets.router)
api_router.include_router(series.router)
api_router.include_router(graph.router)
api_router.include_router(insights.router)
api_router.include_router(copilot.router)
