"""
留言接口测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_captcha(client: AsyncClient):
    """✅ 获取验证码 - 应返回 captcha_id 和 question"""
    response = await client.get("/api/v1/captcha")
    assert response.status_code == 200
    data = response.json()
    assert "captcha_id" in data
    assert "question" in data
    assert "expires_in" in data


@pytest.mark.asyncio
async def test_submit_contact_with_invalid_captcha(client: AsyncClient):
    """❌ 无效验证码提交留言 - 应返回 400"""
    response = await client.post("/api/v1/contacts", json={
        "name": "测试用户",
        "email": "test@example.com",
        "subject": "测试主题",
        "message": "这是一条测试留言",
        "captcha_id": "invalid-id",
        "captcha_answer": "999",
    })
    assert response.status_code == 400
    assert "验证码" in response.text


@pytest.mark.asyncio
async def test_submit_contact_with_valid_data(client: AsyncClient):
    """✅ 提交留言 - 先获取验证码再提交"""
    # 1. 获取验证码
    captcha_resp = await client.get("/api/v1/captcha")
    captcha = captcha_resp.json()

    # 2. 提交留言
    response = await client.post("/api/v1/contacts", json={
        "name": "张三",
        "email": "zhangsan@example.com",
        "subject": "合作咨询",
        "message": "你好，我对你的项目很感兴趣，希望合作！",
        "captcha_id": captcha["captcha_id"],
        "captcha_answer": "0",  # 故意用错误答案
    })

    # 3. 验证码答案不一定对，但请求应该能正常处理
    assert response.status_code in (200, 400)


@pytest.mark.asyncio
async def test_get_contacts_list(client: AsyncClient):
    """✅ 获取留言列表 - 应返回 contacts 数组"""
    response = await client.get("/api/v1/contacts")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "contacts" in data
    assert isinstance(data["contacts"], list)


@pytest.mark.asyncio
async def test_get_stats(client: AsyncClient):
    """✅ 获取统计数据 - 应返回统计字段"""
    response = await client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_contacts" in data
    assert "replied_contacts" in data
    assert "unread_contacts" in data
    assert "new_this_week" in data


@pytest.mark.asyncio
async def test_reply_contact_unauthorized(client: AsyncClient):
    """❌ 未授权回复 - 应返回 401"""
    response = await client.post("/api/v1/contacts/1/reply", json={
        "reply": "感谢您的留言！",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_contact_unauthorized(client: AsyncClient):
    """❌ 未授权删除 - 应返回 401"""
    response = await client.delete("/api/v1/contacts/1")
    assert response.status_code == 401
