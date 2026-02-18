"""Rename tables to coherent singular names

Revision ID: d28b244c29a1
Revises: c3f8a912b047
Create Date: 2026-02-18 07:45:28.913357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd28b244c29a1'
down_revision: Union[str, Sequence[str], None] = 'c3f8a912b047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename all tables to coherent singular names without Table suffix
    op.rename_table('GroupMemberTable', 'GroupMember')
    op.rename_table('GroupTable', 'Group')
    op.rename_table('OwnershipTable', 'Ownership')
    op.rename_table('PasswordTable', 'Password')
    op.rename_table('PermissionsTable', 'Permission')
    op.rename_table('SsoConfigurationTable', 'SsoConfiguration')
    op.rename_table('SsoUsersTable', 'SsoUser')
    op.rename_table('UserPasswordTable', 'UserPassword')
    op.rename_table('UserTable', 'User')
    
    # For tables that only differ in case (vault -> Vault, iam_events -> IamEvent)
    # SQLite treats table names as case-insensitive, so direct rename would fail
    # Other databases (PostgreSQL, MySQL) handle this correctly
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'sqlite':
        # SQLite: use temporary names as intermediate step
        op.rename_table('vault', '_temp_vault')
        op.rename_table('iam_events', '_temp_iam_events')
        op.rename_table('password_events', '_temp_password_events')
        op.rename_table('vault_events', '_temp_vault_events')
        
        op.rename_table('_temp_vault', 'Vault')
        op.rename_table('_temp_iam_events', 'IamEvent')
        op.rename_table('_temp_password_events', 'PasswordEvent')
        op.rename_table('_temp_vault_events', 'VaultEvent')
    else:
        # PostgreSQL and others: direct rename works
        op.rename_table('vault', 'Vault')
        op.rename_table('iam_events', 'IamEvent')
        op.rename_table('password_events', 'PasswordEvent')
        op.rename_table('vault_events', 'VaultEvent')


def downgrade() -> None:
    """Downgrade schema."""
    # Revert table names back to original names
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'sqlite':
        # SQLite: use temporary names as intermediate step
        op.rename_table('VaultEvent', '_temp_vault_events')
        op.rename_table('PasswordEvent', '_temp_password_events')
        op.rename_table('IamEvent', '_temp_iam_events')
        op.rename_table('Vault', '_temp_vault')
        
        op.rename_table('_temp_vault_events', 'vault_events')
        op.rename_table('_temp_password_events', 'password_events')
        op.rename_table('_temp_iam_events', 'iam_events')
        op.rename_table('_temp_vault', 'vault')
    else:
        # PostgreSQL and others: direct rename works
        op.rename_table('VaultEvent', 'vault_events')
        op.rename_table('PasswordEvent', 'password_events')
        op.rename_table('IamEvent', 'iam_events')
        op.rename_table('Vault', 'vault')
    
    # Rename other tables
    op.rename_table('User', 'UserTable')
    op.rename_table('UserPassword', 'UserPasswordTable')
    op.rename_table('SsoUser', 'SsoUsersTable')
    op.rename_table('SsoConfiguration', 'SsoConfigurationTable')
    op.rename_table('Permission', 'PermissionsTable')
    op.rename_table('Password', 'PasswordTable')
    op.rename_table('Ownership', 'OwnershipTable')
    op.rename_table('Group', 'GroupTable')
    op.rename_table('GroupMember', 'GroupMemberTable')
