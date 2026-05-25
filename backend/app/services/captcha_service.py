"""
验证码生成/校验服务
支持内存存储（开发）和 Redis 存储（生产）
"""
import secrets
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

# 内存存储（开发环境）
_captchas: dict[str, dict] = {}


class CaptchaService:
    def __init__(self, use_redis: bool = False):
        self.use_redis = use_redis

    def generate(self) -> dict:
        """生成数学验证码"""
        captcha_id = secrets.token_hex(16)
        a = random.randint(0, 9)
        b = random.randint(0, 9)
        op = random.choice(["+", "-"])

        if op == "+":
            answer = str(a + b)
        else:
            if a < b:
                a, b = b, a
            answer = str(a - b)

        # 存储（5 分钟过期）
        _captchas[captcha_id] = {
            "answer": answer,
            "expires": datetime.now(timezone.utc) + timedelta(minutes=5),
        }

        return {
            "captcha_id": captcha_id,
            "question": f"{a} {op} {b} = ?",
            "expires_in": 300,
        }

    def verify(self, captcha_id: str, answer: str) -> Optional[str]:
        """验证验证码，返回 None 表示通过"""
        captcha_data = _captchas.get(captcha_id)
        if not captcha_data:
            return "验证码已过期，请刷新重试"

        if datetime.now(timezone.utc) > captcha_data["expires"]:
            _captchas.pop(captcha_id, None)
            return "验证码已过期，请刷新重试"

        if captcha_data["answer"] != answer.strip():
            return "验证码错误"

        # 清除已使用的验证码
        _captchas.pop(captcha_id, None)
        return None

    def cleanup_expired(self):
        """清理过期验证码"""
        now = datetime.now(timezone.utc)
        expired = [
            cid for cid, data in _captchas.items()
            if data["expires"] < now
        ]
        for cid in expired:
            _captchas.pop(cid, None)


# 全局单例
captcha_service = CaptchaService()
