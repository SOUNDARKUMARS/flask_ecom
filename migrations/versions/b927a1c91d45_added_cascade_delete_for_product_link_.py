"""Added cascade delete for product_link in Cart

Revision ID: b927a1c91d45
Revises: 1db226bd0709
Create Date: 2024-09-27 18:28:50.337276
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'b927a1c91d45'
down_revision = '1db226bd0709'
branch_labels = None
depends_on = None


def get_constraint_name(table_name, column_name, referenced_table):
    """Helper to find the actual foreign key constraint name."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    foreign_keys = inspector.get_foreign_keys(table_name)

    for fk in foreign_keys:
        if fk['referred_table'] == referenced_table and fk['constrained_columns'] == [column_name]:
            return fk['name']
    return None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        # Retrieve the existing foreign key constraint name
        fk_name = get_constraint_name('cart', 'product_link', 'product')
        
        if fk_name:
            # Drop the foreign key constraint using the retrieved name
            batch_op.drop_constraint(fk_name, type_='foreignkey')
        
        # Recreate the foreign key with cascade delete
        batch_op.create_foreign_key('fk_cart_product_link', 'product', ['product_link'], ['id'], ondelete='cascade')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        # Drop the updated foreign key first
        batch_op.drop_constraint('fk_cart_product_link', type_='foreignkey')
        
        # Recreate the original foreign key without cascade
        batch_op.create_foreign_key('fk_cart_product_link', 'product', ['product_link'], ['id'])

    # ### end Alembic commands ###
