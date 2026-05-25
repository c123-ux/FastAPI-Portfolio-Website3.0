"""
依赖注入 - 统一管理 FastAPI 依赖
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.services.audit_service import AuditService
from app.utils.jwt import get_current_user


async def get_contact_service(db: AsyncSession = Depends(get_db)) -> ContactService:
    """获取留言服务实例"""
    return ContactService(db)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """获取认证服务实例"""
    return AuthService(db)


async def get_email_service() -> EmailService:
    """获取邮件服务实例"""
    return EmailService()


async def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    """获取审计服务实例"""
    return AuditService(db)
