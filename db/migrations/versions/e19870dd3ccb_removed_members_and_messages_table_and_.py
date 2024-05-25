"""Removed members and messages table and everything related

Revision ID: e19870dd3ccb
Revises: 0751ff6478ab
Create Date: 2024-05-23 07:59:55.638006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e19870dd3ccb'
down_revision: Union[str, None] = '0751ff6478ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('member_guild')
    op.drop_table('member_role')
    op.drop_table('member_overwrite')
    op.drop_table('message')
    op.drop_table('member')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('member',
    sa.Column('is_bot', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('display_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('global_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('permissions_value', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('nick', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('id', sa.BIGINT(), server_default=sa.text("nextval('member_id_seq'::regclass)"),
              autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('etl_modified', postgresql.TIMESTAMP(), server_default=sa.text('now()'),
              autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='member_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('member_guild',
    sa.Column('member_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('guild_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['guild_id'], ['guild.id'], name='member_guild_guild_id_fkey'),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], name='member_guild_member_id_fkey'),
    sa.PrimaryKeyConstraint('member_id', 'guild_id', name='member_guild_pkey')
    )
    op.create_table('message',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('message_len', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('member_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('channel_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('edited', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channel.id'], name='message_channel_id_fkey'),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], name='message_member_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='message_pkey')
    )

    op.create_table('member_overwrite',
    sa.Column('channel_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('member_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channel.id'], name='member_overwrite_channel_id_fkey'),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], name='member_overwrite_member_id_fkey'),
    sa.PrimaryKeyConstraint('channel_id', 'member_id', name='member_overwrite_pkey')
    )
    op.create_table('member_role',
    sa.Column('member_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('role_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], name='member_role_member_id_fkey'),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name='member_role_role_id_fkey'),
    sa.PrimaryKeyConstraint('member_id', 'role_id', name='member_role_pkey')
    )
    # ### end Alembic commands ###