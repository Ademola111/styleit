"""empty message

Revision ID: 94bc4c741546
Revises: ba71b07e332c
Create Date: 2023-02-12 20:55:28.495282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94bc4c741546'
down_revision = 'ba71b07e332c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customer', sa.Column('cust_access', sa.Enum('actived', 'deactived'), server_default='deactived', nullable=True))
    op.add_column('designer', sa.Column('desi_access', sa.Enum('actived', 'deactived'), server_default='deactived', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('designer', 'desi_access')
    op.drop_column('customer', 'cust_access')
    # ### end Alembic commands ###
