"""
认证相关路由 - /api/v1/auth
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, PasswordChangeRequest
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.dependencies import get_auth_service, get_audit_service
from app.utils.jwt import get_current_user
from app.middleware.rate_limit import limiter
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    form: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    audit_service: AuditService = Depends(get_audit_service),
):
    """管理员登录"""
    result = await auth_service.authenticate(form.username, form.password)

    # 记录登录审计
    await audit_service.log(
        username=form.username,
        action="login",
        ip_address=request.client.host if request.client else None,
    )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        username=form.username,
    )


@router.post("/refresh", response_model=APIResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    form: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """刷新访问令牌"""
    result = await auth_service.refresh_token(form.refresh_token)
    return APIResponse(data=result)


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    request: Request,
    form: PasswordChangeRequest,
    auth_service: AuthService = Depends(get_auth_service),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
):
    """修改密码（需要认证）"""
    username = current_user.get("sub", "")
    await auth_service.change_password(username, form.old_password, form.new_password)

    await audit_service.log(
        username=username,
        action="change_password",
        ip_address=request.client.host if request.client else None,
    )

    return APIResponse(message="密码修改成功")
