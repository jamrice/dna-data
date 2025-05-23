"""Contents table add column

Revision ID: 1c0fe475349c
Revises: 52cca6abdc27
Create Date: 2025-04-09 12:31:10.592733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c0fe475349c'
down_revision: Union[str, None] = '52cca6abdc27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contents', sa.Column('likes', sa.Integer(), nullable=False))
    op.add_column('contents', sa.Column('unlikes', sa.Integer(), nullable=False))
    op.add_column('contents', sa.Column('comments', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contents', 'comments')
    op.drop_column('contents', 'unlikes')
    op.drop_column('contents', 'likes')
    # ### end Alembic commands ###
