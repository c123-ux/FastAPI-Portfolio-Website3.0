"""
留言业务逻辑
"""
from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contact import Contact
from app.schemas.contact import ContactCreate
from app.utils.security import escape_html


class ContactService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ContactCreate) -> Contact:
        """创建留言（自动转义 HTML 防 XSS）"""
        contact = Contact(
            name=escape_html(data.name),
            email=data.email,
            subject=escape_html(data.subject or "无主题"),
            message=escape_html(data.message),
        )
        self.db.add(contact)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def get_all(self) -> list[Contact]:
        """获取所有留言（按时间倒序）"""
        result = await self.db.execute(
            select(Contact).order_by(Contact.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, contact_id: int) -> Contact | None:
        """根据 ID 获取留言"""
        result = await self.db.execute(
            select(Contact).where(Contact.id == contact_id)
        )
        return result.scalar_one_or_none()

    async def reply(self, contact_id: int, reply_text: str) -> Contact | None:
        """回复留言"""
        contact = await self.get_by_id(contact_id)
        if not contact:
            return None
        from datetime import datetime, timezone
        contact.reply = escape_html(reply_text)
        contact.replied_at = datetime.now(timezone.utc)
        contact.status = "replied"
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact_id: int) -> bool:
        """删除留言"""
        contact = await self.get_by_id(contact_id)
        if not contact:
            return False
        await self.db.delete(contact)
        await self.db.flush()
        return True

    async def get_stats(self) -> dict:
        """获取统计数据"""
        # 总留言数
        result = await self.db.execute(select(func.count(Contact.id)))
        total = result.scalar()

        # 已回复
        result = await self.db.execute(
            select(func.count(Contact.id)).where(Contact.status == "replied")
        )
        replied = result.scalar()

        # 本周新增
        from datetime import datetime, timedelta, timezone
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        result = await self.db.execute(
            select(func.count(Contact.id)).where(Contact.created_at >= week_ago)
        )
        new_this_week = result.scalar()

        # 各状态统计
        result = await self.db.execute(
            select(Contact.status, func.count(Contact.id))
            .group_by(Contact.status)
        )
        status_stats = {row.status: row[1] for row in result}

        return {
            "total_contacts": total,
            "replied_contacts": replied,
            "unread_contacts": status_stats.get("unread", 0),
            "new_this_week": new_this_week,
        }

    async def increment_views(self, contact_id: int):
        """增加留言浏览次数"""
        contact = await self.get_by_id(contact_id)
        if contact:
            contact.views = (contact.views or 0) + 1
            await self.db.flush()
