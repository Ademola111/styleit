"""empty message

Revision ID: 8c2629fa91fa
Revises: 82123325a3ff
Create Date: 2023-01-01 16:24:59.611520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c2629fa91fa'
down_revision = '82123325a3ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin', sa.Column('new_admin_secretword', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('admin', 'new_admin_secretword')
    # ### end Alembic commands ###
