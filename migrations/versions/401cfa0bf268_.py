"""empty message

Revision ID: 401cfa0bf268
Revises: 2cca8fcec783
Create Date: 2021-02-20 15:49:01.335428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '401cfa0bf268'
down_revision = '2cca8fcec783'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_deleted')
    op.drop_column('posts', 'is_deleted')
    # ### end Alembic commands ###
