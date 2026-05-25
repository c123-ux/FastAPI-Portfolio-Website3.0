"""
通用响应模型
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime


class APIResponse(BaseModel):
    """统一 API 响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    timestamp: datetime = None

    model_config = ConfigDict(from_attributes=True)

    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.now()
        super().__init__(**data)


class StatsResponse(BaseModel):
    """统计数据响应"""
    total_contacts: int = 0
    replied_contacts: int = 0
    unread_contacts: int = 0
    unique_visitors_30d: int = 0
    total_page_views: int = 0
    new_this_week: int = 0


class CaptchaResponse(BaseModel):
    """验证码响应"""
    captcha_id: str
    question: str
    expires_in: int = 300
