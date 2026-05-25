"""
安全工具 - 密码哈希、HTML 转义
"""
import html
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """使用 bcrypt 哈希密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def escape_html(text: str) -> str:
    """HTML 转义 - 防止 XSS 攻击"""
    if not text:
        return ""
    return html.escape(text, quote=True)
