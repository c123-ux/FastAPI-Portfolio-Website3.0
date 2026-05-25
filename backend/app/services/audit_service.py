"""
审计日志服务 - 记录管理员操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from typing import Optional


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, username: str, action: str,
                   target_type: Optional[str] = None,
                   target_id: Optional[int] = None,
                   detail: Optional[str] = None,
                   ip_address: Optional[str] = None):
        """记录审计日志"""
        log = AuditLog(
            username=username,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip_address,
        )
        self.db.add(log)
        await self.db.flush()

    async def get_recent(self, limit: int = 50) -> list[AuditLog]:
        """获取最近的审计日志"""
        from sqlalchemy import select
        result = await self.db.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
