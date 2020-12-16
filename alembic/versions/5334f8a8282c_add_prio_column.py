"""
Add "prio" column to "server" table.
Created: 2020-12-15 15:04:49.371802
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5334f8a8282c'
down_revision = 'f62e64b43d2f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('server', sa.Column('prio', sa.Integer(), server_default='10', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('server', 'prio')
    # ### end Alembic commands ###