"""modified email and numeroTelephone to non-nullable columns, added password in Utilisateur

Revision ID: 35ce23b69fe1
Revises: 
Create Date: 2025-06-24 20:49:21.081270

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '35ce23b69fe1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('utilisateur', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(length=65), nullable=False))
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=254),
               nullable=False)
        batch_op.alter_column('numeroTelephone',
               existing_type=mysql.VARCHAR(length=254),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('utilisateur', schema=None) as batch_op:
        batch_op.alter_column('numeroTelephone',
               existing_type=mysql.VARCHAR(length=254),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=254),
               nullable=True)
        batch_op.drop_column('password')

    # ### end Alembic commands ###
