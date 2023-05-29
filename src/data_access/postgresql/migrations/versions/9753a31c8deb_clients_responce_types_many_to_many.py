"""clients_response_types_many_to_many

Revision ID: 9753a31c8deb
Revises: b7dec17bc956
Create Date: 2023-03-23 14:00:21.035627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9753a31c8deb'
down_revision = 'b7dec17bc956'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('response_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type')
    )
    op.create_table('clients_response_types',
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('response_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['response_type_id'], ['response_types.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('client_id', 'response_type_id')
    )
    op.drop_table('clients_granttypes')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clients_granttypes',
    sa.Column('client_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('persistent_grant_type_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], name='clients_granttypes_client_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['persistent_grant_type_id'], ['persistent_grant_types.id'], name='clients_granttypes_persistent_grant_type_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('client_id', 'persistent_grant_type_id', name='clients_granttypes_pkey')
    )
    op.drop_table('clients_response_types')
    op.drop_table('response_types')
    # ### end Alembic commands ###
