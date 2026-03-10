from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text

from app.core.config import get_settings
from app.db.seed import seed_reference_catalog
from app.db.session import get_engine, get_session_factory
from app.services.refresh_scheduler import RefreshScheduler
from app.services.refresh_service import RefreshService


@dataclass
class AppRuntime:
    scheduler: RefreshScheduler | None = None

    def shutdown(self) -> None:
        if self.scheduler is not None:
            self.scheduler.stop()


def initialize_application() -> AppRuntime:
    settings = get_settings()
    engine = get_engine()
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    with get_session_factory()() as session:
        seed_reference_catalog(session)

    refresh_service = RefreshService(get_session_factory())
    if settings.seed_demo_catalog:
        refresh_service.bootstrap_missing_versions()

    scheduler: RefreshScheduler | None = None
    if settings.scheduler_enabled:
        scheduler = RefreshScheduler(
            runner=refresh_service.run_due_refreshes,
            poll_interval_seconds=settings.scheduler_poll_interval_seconds,
        )
        scheduler.start(force_run_on_startup=settings.scheduler_force_run_on_startup)

    return AppRuntime(scheduler=scheduler)
