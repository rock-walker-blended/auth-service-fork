"""created_at change

Revision ID: 1bbf3e5de93d
Revises: dedb0efbd18d
Create Date: 2022-11-24 12:15:32.651998

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1bbf3e5de93d'
down_revision = 'dedb0efbd18d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('client_claims', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('client_claims', 'created')
    op.add_column('client_cors_origins', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('client_cors_origins', 'created')
    op.add_column('client_grant_types', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('client_grant_types', 'created')
    op.add_column('client_id_restrictions', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('client_id_restrictions', 'created')
    op.add_column('client_post_logout_redirect_uris', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('client_post_logout_redirect_uris', 'created')
    op.add_column('client_redirect_uris', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('client_redirect_uris', 'created')
    op.add_column('client_scopes', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('client_scopes', 'created')
    op.add_column('client_secrets', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('client_secrets', 'created')
    op.add_column('clients', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_column('clients', 'created')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clients', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('clients', 'created_at')
    op.add_column('client_secrets', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('client_secrets', 'created_at')
    op.add_column('client_scopes', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('client_scopes', 'created_at')
    op.add_column('client_redirect_uris', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('client_redirect_uris', 'created_at')
    op.add_column('client_post_logout_redirect_uris', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('client_post_logout_redirect_uris', 'created_at')
    op.add_column('client_id_restrictions', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('client_id_restrictions', 'created_at')
    op.add_column('client_grant_types', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('client_grant_types', 'created_at')
    op.add_column('client_cors_origins', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('client_cors_origins', 'created_at')
    op.add_column('client_claims', sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('client_claims', 'created_at')
    # ### end Alembic commands ###