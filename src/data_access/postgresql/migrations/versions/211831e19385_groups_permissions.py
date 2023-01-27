"""Groups Permissions

Revision ID: 211831e19385
Revises: 5785b657a0ec
Create Date: 2023-01-27 10:55:12.174735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '211831e19385'
down_revision = '5785b657a0ec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('parent_group', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_group'], ['groups.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('permissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('permissions_groups',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'permission_id')
    )
    op.create_table('permissions_roles',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    op.create_table('users_groups',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'user_id')
    )
    op.create_table('users_roles',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'user_id')
    )
    op.drop_table('project_team')
    op.alter_column('persistent_grants', 'expiration',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('persistent_grants', 'expiration',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_table('project_team',
    sa.Column('role', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['role'], ['roles.id'], name='project_team_role_fkey'),
    sa.ForeignKeyConstraint(['user'], ['users.id'], name='project_team_user_fkey')
    )
    op.drop_table('users_roles')
    op.drop_table('users_groups')
    op.drop_table('permissions_roles')
    op.drop_table('permissions_groups')
    op.drop_table('permissions')
    op.drop_table('groups')
    # ### end Alembic commands ###
