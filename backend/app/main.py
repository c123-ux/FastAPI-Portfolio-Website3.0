"""
Portfolio Backend v3.0
FastAPI 应用入口 - 模块化分层架构
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_models, engine, AsyncSessionLocal
from app.services.auth_service import AuthService
from app.services.captcha_service import captcha_service
from app.schemas.common import CaptchaResponse
from app.middleware.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期 - 启动和关闭"""
    # 启动时
    print(f"🚀 {settings.APP_NAME} 启动中...")
    print(f"📂 数据库: {settings.DATABASE_URL}")
    print(f"🔐 CORS 白名单: {settings.allowed_origins_list}")

    # 初始化数据库表
    await init_models()

    # 初始化管理员
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        await auth_service.init_admin()
        await session.commit()

    yield

    # 关闭时
    await engine.dispose()
    print("👋 应用已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ===== 中间件配置 =====

# CORS - 白名单模式（替代原来的 allow_origins=["*"]）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# 速率限制
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ===== 全局异常处理 =====


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """统一异常处理 - 返回标准化错误响应"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


# ===== 注册路由 =====
from app.routers import contacts, auth, admin, stats, admin_frontend

app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(stats.router)
app.include_router(admin_frontend.router)


# ===== 公开接口 =====


@app.get("/api/v1/captcha", response_model=CaptchaResponse, tags=["工具"])
async def get_captcha():
    """获取数学验证码"""
    return captcha_service.generate()


@app.get("/api/v1/health", tags=["工具"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "app": settings.APP_NAME,
    }


@app.get("/", tags=["根路径"])
async def root():
    """根路径 - API 概览"""
    return {
        "message": f"{settings.APP_NAME} 运行中",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "3.0.0",
        "endpoints": {
            "验证码": "GET /api/v1/captcha",
            "提交留言": "POST /api/v1/contacts",
            "留言列表": "GET /api/v1/contacts",
            "管理员登录": "POST /api/v1/auth/login",
            "刷新令牌": "POST /api/v1/auth/refresh",
            "数据统计": "GET /api/v1/stats",
            "导出 CSV": "GET /api/v1/admin/export/csv",
            "审计日志": "GET /api/v1/admin/audit-logs",
            "健康检查": "GET /api/v1/health",
        },
    }


# ===== 直接运行 =====
if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print(f"🚀 {settings.APP_NAME}")
    print("=" * 50)
    print(f"📍 API 文档: http://localhost:8000/docs")
    print(f"📍 Redoc:    http://localhost:8000/redoc")
    print(f"📍 健康检查: http://localhost:8000/api/v1/health")
    print("=" * 50)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
