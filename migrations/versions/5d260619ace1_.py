"""empty message

Revision ID: 5d260619ace1
Revises: 3027018ea7ba
Create Date: 2023-04-06 10:32:23.476713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d260619ace1'
down_revision = '3027018ea7ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('bookappointment', sa.Column('ba_paystatus', sa.Enum('pending', 'paid', 'failed'), server_default='pending', nullable=True))
    # ### end Alembic commands ###
    pass


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('bookappointment', 'ba_paystatus')
    # ### end Alembic commands ###
    pass