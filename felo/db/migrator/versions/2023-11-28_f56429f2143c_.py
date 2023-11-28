"""empty message

Revision ID: f56429f2143c
Revises: ccc0e7a299f4
Create Date: 2023-11-28 02:14:29.969261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f56429f2143c'
down_revision = 'ccc0e7a299f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('phrases', sa.Column('phrase_text', sa.String(), nullable=False))
    op.add_column('phrases', sa.Column('phrase_normalized_text', sa.String(), nullable=False))
    op.add_column('phrases', sa.Column('phrase_text_translation', sa.String(), nullable=False))
    op.add_column('phrases', sa.Column('phrase_normalized_text_translation', sa.String(), nullable=False))
    op.drop_column('phrases', 'normalized_text')
    op.drop_column('phrases', 'text')
    op.drop_column('phrases', 'text_translation')
    op.drop_column('phrases', 'normalized_text_translation')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('phrases', sa.Column('normalized_text_translation', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('phrases', sa.Column('text_translation', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('phrases', sa.Column('text', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('phrases', sa.Column('normalized_text', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('phrases', 'phrase_normalized_text_translation')
    op.drop_column('phrases', 'phrase_text_translation')
    op.drop_column('phrases', 'phrase_normalized_text')
    op.drop_column('phrases', 'phrase_text')
    # ### end Alembic commands ###
