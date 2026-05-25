"""
速率限制中间件（使用 slowapi）
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

limiter = Limiter(key_func=get_remote_address)
