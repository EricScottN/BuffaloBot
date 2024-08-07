"""Create a baseline migration

Revision ID: 0751ff6478ab
Revises: 
Create Date: 2024-05-22 21:59:00.481574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0751ff6478ab'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('member_guild')
    op.create_table('member_role')
    op.create_table('member_overwrite')
    op.create_table('message')
    op.create_table('member')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
