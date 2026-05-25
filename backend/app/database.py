"""
异步数据库引擎 - 支持 SQLite(开发)/PostgreSQL(生产)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    """FastAPI 依赖注入 - 获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_models():
    """开发环境自动建表（生产环境使用 Alembic 迁移）"""
    async with engine.begin() as conn:
        from app.models.contact import Contact  # noqa
        from app.models.user import User        # noqa
        from app.models.audit import AuditLog   # noqa
        await conn.run_sync(Base.metadata.create_all)
