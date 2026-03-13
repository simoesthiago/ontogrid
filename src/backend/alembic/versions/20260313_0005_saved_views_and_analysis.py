from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260313_0005"
down_revision = "20260311_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_user",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "saved_view",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("scope_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_saved_view_scope", "saved_view", ["user_id", "scope_type", "scope_id"], unique=False)
    op.create_index("ix_saved_view_updated_at", "saved_view", ["updated_at"], unique=False)
    op.create_index("ix_saved_view_user_id", "saved_view", ["user_id"], unique=False)
    op.create_index("ix_saved_view_scope_id", "saved_view", ["scope_id"], unique=False)
    op.create_index("ix_saved_view_scope_type", "saved_view", ["scope_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_saved_view_scope_type", table_name="saved_view")
    op.drop_index("ix_saved_view_scope_id", table_name="saved_view")
    op.drop_index("ix_saved_view_user_id", table_name="saved_view")
    op.drop_index("ix_saved_view_updated_at", table_name="saved_view")
    op.drop_index("ix_saved_view_scope", table_name="saved_view")
    op.drop_table("saved_view")
    op.drop_table("app_user")
