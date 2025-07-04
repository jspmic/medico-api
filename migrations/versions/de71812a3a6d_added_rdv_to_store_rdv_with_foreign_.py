"""added RDV to store rdv with foreign keys from Utilisateur, Hopital and Service

Revision ID: de71812a3a6d
Revises: 9f1168e8ee9c
Create Date: 2025-07-02 14:21:35.145330

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de71812a3a6d'
down_revision = '9f1168e8ee9c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rdv',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nom', sa.String(length=254), nullable=False),
    sa.Column('sexe', sa.String(length=1), nullable=False),
    sa.Column('dateTime', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('utilisateur_service_hopital',
    sa.Column('utilisateur_id', sa.Integer(), nullable=True),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('hopital_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['hopital_id'], ['hopital.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('utilisateur_service_hopital')
    op.drop_table('rdv')
    # ### end Alembic commands ###
