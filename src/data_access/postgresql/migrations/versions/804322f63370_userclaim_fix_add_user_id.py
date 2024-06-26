"""userclaim-fix-add-user_id

Revision ID: 804322f63370
Revises: 007a74292339
Create Date: 2022-12-06 10:51:08.708358

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '804322f63370'
down_revision = '007a74292339'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_claims', sa.Column('User', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user_claims', 'users', ['User'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_claims', type_='foreignkey')
    op.drop_column('user_claims', 'User')
    # ### end Alembic commands ###
