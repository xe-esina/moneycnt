"""delete email and role

Revision ID: 508e0f4c1ff2
Revises: d354fd98ff7b
Create Date: 2019-12-21 21:54:33.268781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '508e0f4c1ff2'
down_revision = 'd354fd98ff7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_index('ix_users_email')
        batch_op.drop_column('role')
        batch_op.drop_column('email')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.VARCHAR(length=120), nullable=False))
    op.add_column('users', sa.Column('role', sa.SMALLINT(), nullable=True))
    op.create_index('ix_users_email', 'users', ['email'], unique=1)
    # ### end Alembic commands ###
