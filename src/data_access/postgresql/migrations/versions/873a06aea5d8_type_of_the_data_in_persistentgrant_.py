"""Type of the data in PersistentGrant changed from JSON to str

Revision ID: 873a06aea5d8
Revises: 2735607536df
Create Date: 2022-12-16 14:51:04.523499

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '873a06aea5d8'
down_revision = '804322f63370'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('persistent_grants', 'data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               type_=sa.String(length=2048),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('persistent_grants', 'data',
               existing_type=sa.String(length=2048),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=False)
    # ### end Alembic commands ###
