"""empty message

Revision ID: 7ab3e134c2a7
Revises: 9b9c6c6b77d8
Create Date: 2021-03-27 11:02:23.943924

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7ab3e134c2a7'
down_revision = '9b9c6c6b77d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_Users_email', table_name='Users')
    op.drop_index('ix_Users_username', table_name='Users')
    op.drop_table('Users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Users_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('user_type', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('phone', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('approved', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='Users_pkey')
    )
    op.create_index('ix_Users_username', 'Users', ['username'], unique=True)
    op.create_index('ix_Users_email', 'Users', ['email'], unique=True)
    # ### end Alembic commands ###