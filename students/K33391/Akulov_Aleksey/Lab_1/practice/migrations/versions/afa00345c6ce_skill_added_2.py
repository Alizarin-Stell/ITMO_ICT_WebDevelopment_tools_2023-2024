

"""skill added 2

Revision ID: afa00345c6ce
Revises: 667525f8bf76
Create Date: 2024-03-25 01:04:31.709836

"""
from typing import Sequence, Union
import sqlmodel

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afa00345c6ce'
down_revision: Union[str, None] = '667525f8bf76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('skillwarriorlink', sa.Column('level', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('skillwarriorlink', 'level')
    # ### end Alembic commands ###
