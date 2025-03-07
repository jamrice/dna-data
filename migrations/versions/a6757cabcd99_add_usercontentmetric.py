"""Add: UserContentMetric

Revision ID: a6757cabcd99
Revises: 99d52c215ca1
Create Date: 2025-03-07 22:49:51.217641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'a6757cabcd99'
down_revision: Union[str, None] = '99d52c215ca1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_content_metrics',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content_id', sa.String(length=255), nullable=False),
    sa.Column('metric_score', sa.Float(), nullable=False),
    sa.Column('update_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_content_metrics')),
    sa.UniqueConstraint('user_id', 'content_id', name=op.f('uq_user_content_metrics_user_id'))
    )
    op.drop_index('uq_bills_similarity_bill_id', table_name='bills_similarity')
    op.drop_table('bills_similarity')
    op.drop_index('fk_bills_embedding_bills_embedding_bill_id_bills', table_name='bills_embedding')
    op.create_foreign_key(op.f('fk_bills_embedding_bills_embedding_bill_id_bills'), 'bills_embedding', 'bills', ['bill_id'], ['bill_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_bills_embedding_bills_embedding_bill_id_bills'), 'bills_embedding', type_='foreignkey')
    op.create_index('fk_bills_embedding_bills_embedding_bill_id_bills', 'bills_embedding', ['bill_id'], unique=False)
    op.create_table('bills_similarity',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('bill_id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('similarity_bill_id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('similarity_score', mysql.FLOAT(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('uq_bills_similarity_bill_id', 'bills_similarity', ['bill_id', 'similarity_bill_id'], unique=True)
    op.drop_table('user_content_metrics')
    # ### end Alembic commands ###
