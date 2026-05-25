"""
Contact ORM 模型 - 联系表单留言
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    subject = Column(String(200), nullable=True, default="无主题")
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="unread", index=True)
    reply = Column(Text, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    views = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
