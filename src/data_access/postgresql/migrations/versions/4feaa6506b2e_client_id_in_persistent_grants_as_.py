"""client_id in persistent_grants as Integer

Revision ID: 4feaa6506b2e
Revises: 2efbc00f79d7
Create Date: 2023-02-14 10:41:22.692833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4feaa6506b2e'
down_revision = '2efbc00f79d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('persistent_grants', sa.Column('client_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'persistent_grants', 'clients', ['client_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'persistent_grants', type_='foreignkey')
    op.drop_column('persistent_grants', 'client_id')
    # ### end Alembic commands ###
