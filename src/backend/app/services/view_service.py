from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import AppUser, SavedView
from app.services.catalog_service import to_iso8601

UNSET = object()


def _display_name_from_user_id(user_id: str) -> str:
    return user_id.replace("-", " ").replace("_", " ").title()


class ViewService:
    def ensure_user(self, session: Session, user_id: str) -> AppUser:
        user = session.get(AppUser, user_id)
        if user is not None:
            return user

        user = AppUser(
            id=user_id,
            email=None,
            display_name=_display_name_from_user_id(user_id),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def list_views(
        self,
        session: Session,
        *,
        user_id: str,
        scope_type: str,
        scope_id: str,
    ) -> tuple[list[dict[str, object]], int]:
        self.ensure_user(session, user_id)
        query = (
            select(SavedView)
            .where(
                SavedView.user_id == user_id,
                SavedView.scope_type == scope_type,
                SavedView.scope_id == scope_id,
            )
            .order_by(SavedView.updated_at.desc(), SavedView.created_at.desc())
        )
        total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
        items = session.scalars(query).all()
        return [self._serialize(item) for item in items], total

    def create_view(
        self,
        session: Session,
        *,
        user_id: str,
        scope_type: str,
        scope_id: str,
        name: str,
        description: str | None,
        config_json: dict[str, object],
    ) -> dict[str, object]:
        self.ensure_user(session, user_id)
        view = SavedView(
            id=str(uuid4()),
            user_id=user_id,
            scope_type=scope_type,
            scope_id=scope_id,
            name=name.strip(),
            description=description,
            config_json=config_json,
        )
        session.add(view)
        session.commit()
        session.refresh(view)
        return self._serialize(view)

    def update_view(
        self,
        session: Session,
        *,
        user_id: str,
        view_id: str,
        name: str | None | object = UNSET,
        description: str | None | object = UNSET,
        config_json: dict[str, object] | None | object = UNSET,
    ) -> dict[str, object] | None:
        self.ensure_user(session, user_id)
        view = session.scalar(select(SavedView).where(SavedView.id == view_id, SavedView.user_id == user_id))
        if view is None:
            return None
        if name is not UNSET:
            normalized_name = str(name).strip() if name is not None else ""
            if normalized_name:
                view.name = normalized_name
        if description is not UNSET:
            view.description = description if isinstance(description, str) or description is None else str(description)
        if config_json is not UNSET:
            view.config_json = dict(config_json) if isinstance(config_json, dict) else {}
        session.commit()
        session.refresh(view)
        return self._serialize(view)

    def delete_view(self, session: Session, *, user_id: str, view_id: str) -> bool:
        self.ensure_user(session, user_id)
        view = session.scalar(select(SavedView).where(SavedView.id == view_id, SavedView.user_id == user_id))
        if view is None:
            return False
        session.delete(view)
        session.commit()
        return True

    def get_view(self, session: Session, *, user_id: str, view_id: str) -> dict[str, object] | None:
        self.ensure_user(session, user_id)
        view = session.scalar(select(SavedView).where(SavedView.id == view_id, SavedView.user_id == user_id))
        if view is None:
            return None
        return self._serialize(view)

    def _serialize(self, item: SavedView) -> dict[str, object]:
        return {
            "id": item.id,
            "user_id": item.user_id,
            "scope_type": item.scope_type,
            "scope_id": item.scope_id,
            "name": item.name,
            "description": item.description,
            "config_json": dict(item.config_json or {}),
            "created_at": to_iso8601(item.created_at) or "",
            "updated_at": to_iso8601(item.updated_at) or "",
        }


view_service = ViewService()
