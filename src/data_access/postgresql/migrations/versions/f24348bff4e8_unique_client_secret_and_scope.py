"""unique client secret and scope

Revision ID: f24348bff4e8
Revises: 885a98137552
Create Date: 2023-03-23 12:42:37.108071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f24348bff4e8'
down_revision = '7a5ee88941c1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'client_scopes', ['client_id'])
    op.create_unique_constraint(None, 'client_secrets', ['client_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'client_secrets', type_='unique')
    op.drop_constraint(None, 'client_scopes', type_='unique')
    # ### end Alembic commands ###