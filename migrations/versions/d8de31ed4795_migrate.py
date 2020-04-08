"""Migrate

Revision ID: d8de31ed4795
Revises: d92e55f1ccf4
Create Date: 2020-04-08 22:34:19.898536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8de31ed4795'
down_revision = 'd92e55f1ccf4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content', sa.Text(), nullable=True))
        batch_op.drop_column('content_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_url', sa.TEXT(), nullable=True))
        batch_op.drop_column('content')

    # ### end Alembic commands ###
