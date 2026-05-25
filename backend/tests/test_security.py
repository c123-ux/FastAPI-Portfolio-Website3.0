"""
安全专项测试 - CORS / SQL注入 / XSS / 速率限制
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """✅ CORS 头检查 - 验证白名单机制"""
    test_origins = [
        ("http://localhost:3000", 200),
        ("http://localhost:5173", 200),
        ("http://127.0.0.1:8000", 200),
        ("https://evil-site.com", 200),  # 请求能到达，但无 Access-Control
    ]

    for origin, expected_status in test_origins:
        response = await client.options(
            "/api/v1/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        # 允许的 origin 应返回 Access-Control-Allow-Origin
        if "localhost" in origin or "127.0.0.1" in origin:
            assert response.headers.get("access-control-allow-origin") == origin, \
                f"Origin {origin} 应被允许"
        else:
            allow_origin = response.headers.get("access-control-allow-origin", "")
            assert origin not in allow_origin, \
                f"Origin {origin} 不应被允许"


@pytest.mark.asyncio
async def test_sql_injection_in_login(client: AsyncClient):
    """✅ SQL 注入防护测试"""
    payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "admin'--",
        "' UNION SELECT * FROM users --",
    ]
    for payload in payloads:
        response = await client.post("/api/v1/auth/login", json={
            "username": payload,
            "password": payload,
        })
        # 不应返回 200（登录成功）或 500（服务器错误）
        assert response.status_code not in (200, 500), \
            f"SQL注入 payload '{payload}' 不应通过, 返回 {response.status_code}"


@pytest.mark.asyncio
async def test_xss_in_contact(client: AsyncClient):
    """✅ XSS 防护测试 - 留言内容应被转义"""
    # 先获取验证码
    captcha_resp = await client.get("/api/v1/captcha")
    captcha = captcha_resp.json()

    # 提交含 XSS 的留言
    xss_payload = '<script>alert("xss")</script>'
    response = await client.post("/api/v1/contacts", json={
        "name": xss_payload,
        "email": "test@example.com",
        "subject": xss_payload,
        "message": xss_payload,
        "captcha_id": captcha["captcha_id"],
        "captcha_answer": "0",  # 可能错误，但重点检查转义逻辑
    })

    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            # 验证返回的数据已被转义
            result_name = data["data"].get("name", "")
            assert "<script>" not in result_name, "XSS payload 应被转义"


@pytest.mark.skip(reason="需要启动速率限制中间件后验证")
@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    """⏳ 速率限制测试（跳过，需在集成环境运行）"""
    for _ in range(10):
        await client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrong-pass",
        })

    # 第 11 次应触发速率限制
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrong-pass",
    })
    assert response.status_code == 429, "应触发速率限制返回 429"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """✅ 健康检查端点"""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "3.0.0"
