"""Add login field for user

Revision ID: f9398e8b8bb4
Revises: ab7680a432e1
Create Date: 2020-04-01 12:40:53.123055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9398e8b8bb4'
down_revision = 'ab7680a432e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('login', sa.String(), nullable=True))
    op.create_index(op.f('ix_user_login'), 'user', ['login'], unique=True)
    op.drop_index('ix_user_username', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_username', 'user', ['username'], unique=1)
    op.drop_index(op.f('ix_user_login'), table_name='user')
    op.drop_column('user', 'login')
    # ### end Alembic commands ###