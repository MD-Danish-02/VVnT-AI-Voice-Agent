"""add lead owner

Revision ID: 0003_add_lead_owner
Revises: 0002_initial_models
Create Date: 2026-09-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0003_add_lead_owner"
down_revision = "0002_initial_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(op.f("ix_leads_owner_id"), "leads", ["owner_id"], unique=False)
    op.create_foreign_key(
        "fk_leads_owner_id_users",
        "leads",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_leads_owner_id_users", "leads", type_="foreignkey")
    op.drop_index(op.f("ix_leads_owner_id"), table_name="leads")
    op.drop_column("leads", "owner_id")
