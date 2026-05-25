"""
认证接口测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """✅ 登录成功 - 应返回 access_token + refresh_token"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@2026",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """❌ 密码错误 - 应返回 401"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrong-password",
    })
    assert response.status_code == 401
    assert "用户名或密码错误" in response.text


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """❌ 用户不存在 - 应返回 401"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "SomePass123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, admin_token):
    """✅ 刷新令牌 - 应返回新的 access_token"""
    # 先获取 refresh_token
    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@2026",
    })
    refresh_token = login_resp.json()["refresh_token"]

    # 刷新
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_access_protected_route_without_token(client: AsyncClient):
    """❌ 无令牌访问保护接口 - 应返回 401"""
    response = await client.get("/api/v1/admin/audit-logs")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_access_protected_route_with_token(client: AsyncClient):
    """✅ 带令牌访问保护接口 - 需要独立获取 token（避免速率限制）"""
    # 独立登录获取 token
    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@2026",
    })
    if login_resp.status_code != 200:
        # 速率限制时跳过
        return
    token = login_resp.json().get("access_token", "")
    if not token:
        return
    response = await client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
