"""id_update

Revision ID: f217db047f72
Revises: c9363d376df0
Create Date: 2023-05-18 12:22:11.583729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f217db047f72'
down_revision = 'c9363d376df0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('persistent_grant_types', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('persistent_grant_types', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('refresh_token_expiration_types', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('refresh_token_expiration_types', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('refresh_token_usage_types', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('refresh_token_usage_types', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('refresh_token_usage_types', 'updated_at')
    op.drop_column('refresh_token_usage_types', 'created_at')
    op.drop_column('refresh_token_expiration_types', 'updated_at')
    op.drop_column('refresh_token_expiration_types', 'created_at')
    op.drop_column('persistent_grant_types', 'updated_at')
    op.drop_column('persistent_grant_types', 'created_at')
    # ### end Alembic commands ###
