"""empty message

Revision ID: 5fc5abe6245c
Revises: f56429f2143c
Create Date: 2023-11-28 20:21:55.317075

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fc5abe6245c'
down_revision = 'f56429f2143c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lookup', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lookup', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###