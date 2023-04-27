"""IdentityProviders

Revision ID: b5fab5d6a04a
Revises: 1f1892803806
Create Date: 2023-02-16 16:02:22.006481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5fab5d6a04a'
down_revision = '1f1892803806'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('identity_providers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('auth_endpoint_link', sa.String(), nullable=False),
    sa.Column('token_endpoint_link', sa.String(), nullable=False),
    sa.Column('userinfo_link', sa.String(), nullable=False),
    sa.Column('internal_redirect_uri', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('identity_providers_mapped',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('identity_provider_id', sa.Integer(), nullable=False),
    sa.Column('provider_client_id', sa.String(), nullable=False),
    sa.Column('provider_client_secret', sa.String(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['identity_provider_id'], ['identity_providers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('identity_provider_id')
    )
    op.alter_column('devices', 'client_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('devices', 'client_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_table('identity_providers_mapped')
    op.drop_table('identity_providers')
    # ### end Alembic commands ###