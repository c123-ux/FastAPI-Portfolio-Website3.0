"""
自定义校验器
"""
from typing import Optional


def validate_captcha_answer(answer: str) -> Optional[str]:
    """验证码答案校验"""
    if not answer or not answer.strip():
        return "验证码答案不能为空"
    if not answer.strip().isdigit():
        return "验证码答案必须为数字"
    return None


def validate_contact_message(message: str) -> Optional[str]:
    """留言内容安全校验"""
    if not message:
        return "留言内容不能为空"
    if len(message) > 5000:
        return "留言内容不能超过 5000 字"
    suspicious = ["<script", "javascript:", "onerror=", "onload="]
    for s in suspicious:
        if s.lower() in message.lower():
            return "留言内容包含不允许的 HTML 标签"
    return None
