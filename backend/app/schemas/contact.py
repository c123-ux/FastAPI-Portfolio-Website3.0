"""
Contact Pydantic Schemas - 请求/响应模型
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ContactCreate(BaseModel):
    """创建留言请求"""
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    email: EmailStr = Field(..., description="邮箱")
    subject: Optional[str] = Field(default="无主题", max_length=200, description="主题")
    message: str = Field(..., min_length=1, max_length=5000, description="留言内容")
    captcha_id: str = Field(..., description="验证码 ID")
    captcha_answer: str = Field(..., description="验证码答案")


class ContactReply(BaseModel):
    """回复留言请求"""
    reply: str = Field(..., min_length=1, max_length=5000, description="回复内容")


class ContactResponse(BaseModel):
    """留言响应模型"""
    id: int
    name: str
    email: str
    subject: Optional[str]
    message: str
    status: str
    reply: Optional[str] = None
    replied_at: Optional[datetime] = None
    views: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ContactListResponse(BaseModel):
    """留言列表响应"""
    success: bool = True
    count: int
    contacts: list[ContactResponse]
