"""
认证业务逻辑 - 登录、密码管理
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.user import User
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_token_pair, verify_token, create_access_token
from app.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, username: str, password: str) -> dict:
        """验证用户凭证并返回令牌对"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        return create_token_pair(username)

    async def init_admin(self):
        """初始化默认管理员（启动时调用）"""
        result = await self.db.execute(
            select(User).where(User.username == settings.ADMIN_USERNAME)
        )
        if result.scalar_one_or_none():
            return

        admin = User(
            username=settings.ADMIN_USERNAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
        )
        self.db.add(admin)
        await self.db.flush()
        print(f"✅ 管理员账户已创建: {settings.ADMIN_USERNAME}")

    async def refresh_token(self, refresh_token: str) -> dict:
        """使用刷新令牌获取新的访问令牌"""
        payload = verify_token(refresh_token, "refresh")
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="无效的刷新令牌")

        # 验证用户仍存在
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=401, detail="用户不存在")

        data = {"sub": username}
        return {
            "access_token": create_access_token(data),
            "token_type": "Bearer",
        }

    async def change_password(
        self, username: str, old_password: str, new_password: str
    ) -> bool:
        """修改密码"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="原密码错误")

        user.hashed_password = hash_password(new_password)
        await self.db.flush()
        return True
