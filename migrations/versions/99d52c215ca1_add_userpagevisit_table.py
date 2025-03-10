"""Add: UserPageVisit table

Revision ID: 99d52c215ca1
Revises: ce0a18091c68
Create Date: 2025-03-03 21:35:52.439657

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "99d52c215ca1"
down_revision: Union[str, None] = "ce0a18091c68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_page_visits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("page_id", sa.Text(), nullable=False),
        sa.Column("visit_time", sa.Integer(), nullable=False),
        sa.Column("visited_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_page_visits")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_page_visits")
    # ### end Alembic commands ###
