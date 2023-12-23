"""empty message

Revision ID: 7742c7b2e650
Revises: c750b822ede9
Create Date: 2023-12-18 20:28:21.349892

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7742c7b2e650"
down_revision = "c750b822ede9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "lookup", sa.Column("text_start_position", sa.Integer(), nullable=False)
    )
    op.create_unique_constraint(op.f("uq__lookup__id"), "lookup", ["id"])
    op.create_unique_constraint(op.f("uq__lookup_answer__id"), "lookup_answer", ["id"])
    op.create_unique_constraint(op.f("uq__phrases__id"), "phrases", ["id"])
    op.create_unique_constraint(op.f("uq__token__id"), "token", ["id"])
    op.create_unique_constraint(op.f("uq__user__id"), "user", ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("uq__user__id"), "user", type_="unique")
    op.drop_constraint(op.f("uq__token__id"), "token", type_="unique")
    op.drop_constraint(op.f("uq__phrases__id"), "phrases", type_="unique")
    op.drop_constraint(op.f("uq__lookup_answer__id"), "lookup_answer", type_="unique")
    op.drop_constraint(op.f("uq__lookup__id"), "lookup", type_="unique")
    op.drop_column("lookup", "text_start_position")
    # ### end Alembic commands ###