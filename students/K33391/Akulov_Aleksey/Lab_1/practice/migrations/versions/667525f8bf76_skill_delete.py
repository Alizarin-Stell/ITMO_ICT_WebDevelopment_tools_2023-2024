

"""skill delete

Revision ID: 667525f8bf76
Revises: 4f48840bd3fb
Create Date: 2024-03-25 01:04:09.124551

"""
from typing import Sequence, Union
import sqlmodel

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '667525f8bf76'
down_revision: Union[str, None] = '4f48840bd3fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('skillwarriorlink', 'level')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('skillwarriorlink', sa.Column('level', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
