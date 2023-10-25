"""Initialize

Revision ID: 00f9abfd6efa
Revises: de8c6d660bf3
Create Date: 2023-10-24 14:47:27.764703

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '00f9abfd6efa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def load_sql(filename):
    with open(filename, 'r') as file:
        return file.read()


def upgrade():
    sql = load_sql("alembic/versions/00f9abfd6efa_initialize_upgrade.sql")
    op.execute(sql)


def downgrade():
    sql = load_sql("alembic/versions/00f9abfd6efa_initialize_downgrade.sql")
    op.execute(sql)
