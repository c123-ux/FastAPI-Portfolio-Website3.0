"""
统计相关路由 - /api/v1/stats
"""
from fastapi import APIRouter, Depends
from app.schemas.common import StatsResponse
from app.services.contact_service import ContactService
from app.dependencies import get_contact_service

router = APIRouter(prefix="/api/v1/stats", tags=["统计"])


@router.get("", response_model=StatsResponse)
async def get_stats(
    contact_service: ContactService = Depends(get_contact_service),
):
    """获取网站统计数据"""
    stats = await contact_service.get_stats()
    return StatsResponse(**stats)
