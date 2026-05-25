"""初始迁移 - 创建所有表
Revision ID: 0001
Revises:
Create Date: 2026-05-25
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # contacts 表
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(200), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="unread"),
        sa.Column("reply", sa.Text(), nullable=True),
        sa.Column("replied_at", sa.DateTime(), nullable=True),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contacts_id"), "contacts", ["id"])
    op.create_index(op.f("ix_contacts_email"), "contacts", ["email"])
    op.create_index(op.f("ix_contacts_name"), "contacts", ["name"])
    op.create_index(op.f("ix_contacts_status"), "contacts", ["status"])

    # users 表
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"])
    op.create_index(op.f("ix_users_username"), "users", ["username"])

    # audit_logs 表
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=True),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"])
    op.create_index(op.f("ix_audit_logs_username"), "audit_logs", ["username"])
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_username"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_contacts_status"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_name"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_email"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_id"), table_name="contacts")
    op.drop_table("contacts")
