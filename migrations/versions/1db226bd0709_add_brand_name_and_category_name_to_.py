"""Add brand_name and category_name to Product

Revision ID: 1db226bd0709
Revises: 
Create Date: 2024-09-18 08:34:56.904122

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1db226bd0709'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('brand_name', sa.String(length=40), nullable=False,server_default='Unknown'))
        batch_op.add_column(sa.Column('category_name', sa.String(length=40), nullable=False, server_default='Uncategorized'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('category_name')
        batch_op.drop_column('brand_name')

    # ### end Alembic commands ###
