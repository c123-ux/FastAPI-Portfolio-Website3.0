"""
标准 JWT 工具封装（使用 python-jose）
替代原来的手写 SHA-256 + Base64
"""
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer(auto_error=True)


def create_access_token(data: dict) -> str:
    """创建访问令牌（短时效）"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """创建刷新令牌（长时效）"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> dict:
    """验证 JWT 令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="令牌类型无效")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI 依赖注入 - 从请求头获取当前用户"""
    return verify_token(credentials.credentials, "access")


def create_token_pair(username: str) -> dict:
    """创建令牌对（access + refresh）"""
    data = {"sub": username}
    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token(data),
        "token_type": "Bearer",
    }
