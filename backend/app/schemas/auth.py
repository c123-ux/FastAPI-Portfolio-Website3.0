"""
Auth Pydantic Schemas - 认证请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=100, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class TokenResponse(BaseModel):
    """令牌响应"""
    success: bool = True
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    username: str


class RefreshRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")
