"""empty message

Revision ID: 1144b575ea3d
Revises: c7e38c3eed4e
Create Date: 2023-02-21 23:50:24.976134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1144b575ea3d'
down_revision = 'c7e38c3eed4e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorites', schema=None) as batch_op:
        batch_op.alter_column('planet_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorites', schema=None) as batch_op:
        batch_op.alter_column('planet_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
