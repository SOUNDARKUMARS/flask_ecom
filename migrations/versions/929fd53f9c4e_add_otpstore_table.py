"""Add OTPStore table

Revision ID: 929fd53f9c4e
Revises: b927a1c91d45
Create Date: 2024-09-28 19:05:53.864828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '929fd53f9c4e'
down_revision = 'b927a1c91d45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('otp_store',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('otp', sa.String(length=6), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('otp_store')
    # ### end Alembic commands ###
