"""add chat_id to customer"""
revision = 'addchatid20240605'
down_revision = '25a64d6c751d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('customers', sa.Column('chat_id', sa.String(length=32)))

def downgrade():
    op.drop_column('customers', 'chat_id') 