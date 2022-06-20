"""empty message

Revision ID: 6a1300dd4294
Revises: 922654622a40
Create Date: 2022-06-19 21:04:48.324031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a1300dd4294'
down_revision = '922654622a40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'users', ['username'])
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role_id', sa.INTEGER(), nullable=True))
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])
    op.drop_constraint(None, 'users', type_='unique')
    # ### end Alembic commands ###
