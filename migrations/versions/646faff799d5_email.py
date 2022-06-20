"""email

Revision ID: 646faff799d5
Revises: 34a70c1a2d8b
Create Date: 2022-06-16 10:56:27.560939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '646faff799d5'
down_revision = '34a70c1a2d8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookings', sa.Column('email', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_bookings_email'), 'bookings', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bookings_email'), table_name='bookings')
    op.drop_column('bookings', 'email')
    # ### end Alembic commands ###
