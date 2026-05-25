"""
应用配置管理 - 使用 pydantic-settings
生产环境强制校验 SECRET_KEY 和强密码，否则拒绝启动
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Portfolio API v3.0"
    DEBUG: bool = False

    # 数据库 - 开发用 SQLite+aiosqlite，生产用 PostgreSQL+asyncpg
    DATABASE_URL: str = "sqlite+aiosqlite:///./contacts.db"

    # Redis（生产环境验证码/限流/令牌刷新）
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 配置
    SECRET_KEY: str = Field(default="change-me-in-production", min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 管理员账户
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = Field(default="admin123", min_length=8)

    # SMTP 邮件配置（可选）
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_PORT: int = 465
    SENDER_EMAIL: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None
    RECIPIENT_EMAIL: Optional[str] = None

    # CORS 白名单（逗号分隔）
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:63342,http://127.0.0.1:8000"

    # 速率限制
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_CONTACT: str = "10/minute"
    RATE_LIMIT_CAPTCHA: str = "20/minute"

    @property
    def allowed_origins_list(self) -> list:
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        # 开发环境支持 file:// 和 PyCharm Live Preview
        if self.DEBUG:
            origins.append("file://")
            origins.append("null")
            origins.append("http://localhost:63342")
        return origins

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if v == "change-me-in-production" or len(v) < 32:
            raise ValueError(
                "SECRET_KEY 不能使用默认值，且长度至少 32 位. "
                "生产环境请设置强随机密钥: openssl rand -hex 32"
            )
        return v

    @field_validator("ADMIN_PASSWORD")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("密码长度至少 8 位")
        if not any(c.isupper() for c in v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含至少一个数字")
        return v

    @property
    def is_postgres(self) -> bool:
        return "postgresql" in self.DATABASE_URL

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
