"""empty message

Revision ID: 3b53561678bc
Revises: 0efb74e4aee0
Create Date: 2023-11-03 18:29:25.110797

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b53561678bc'
down_revision = '0efb74e4aee0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('username', sa.TEXT(), nullable=False),
    sa.Column('password', sa.TEXT(), nullable=False),
    sa.Column('email', sa.TEXT(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('dt_created', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('dt_updated', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__user')),
    sa.UniqueConstraint('id', name=op.f('uq__user__id'))
    )
    op.create_index(op.f('ix__user__password'), 'user', ['password'], unique=False)
    op.create_index(op.f('ix__user__username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix__user__username'), table_name='user')
    op.drop_index(op.f('ix__user__password'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
