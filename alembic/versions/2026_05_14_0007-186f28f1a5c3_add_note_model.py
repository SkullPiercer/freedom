"""Add Note model

Revision ID: 186f28f1a5c3
Revises: 4b41b29c261a
Create Date: 2026-05-14 00:07:04.327600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '186f28f1a5c3'
down_revision: Union[str, Sequence[str], None] = '4b41b29c261a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('is_archived', sa.Boolean(), nullable=False),
    sa.Column('archived_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_note_is_archived'), 'note', ['is_archived'], unique=False)
    op.create_index(op.f('ix_note_title'), 'note', ['title'], unique=False)
    op.create_index(op.f('ix_note_user_id'), 'note', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_note_user_id'), table_name='note')
    op.drop_index(op.f('ix_note_title'), table_name='note')
    op.drop_index(op.f('ix_note_is_archived'), table_name='note')
    op.drop_table('note')
