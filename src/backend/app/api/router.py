from fastapi import APIRouter

from app.api.routes import datasets, graph, series, sources


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(sources.router)
api_router.include_router(datasets.router)
api_router.include_router(series.router)
api_router.include_router(graph.router)
