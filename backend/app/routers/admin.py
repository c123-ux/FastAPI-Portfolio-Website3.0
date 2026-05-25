"""
管理后台路由 - /api/v1/admin
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from app.schemas.common import APIResponse
from app.services.contact_service import ContactService
from app.services.audit_service import AuditService
from app.dependencies import get_contact_service, get_audit_service
from app.utils.jwt import get_current_user
import csv
import io
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/admin", tags=["管理"])


@router.get("/export/csv", response_class=Response)
async def export_csv(
    request: Request,
    contact_service: ContactService = Depends(get_contact_service),
    current_user: dict = Depends(get_current_user),
):
    """导出留言数据为 CSV（需要认证）"""
    contacts = await contact_service.get_all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "姓名", "邮箱", "主题", "留言", "状态", "回复", "时间"])

    for c in contacts:
        writer.writerow([
            c.id, c.name, c.email, c.subject or "",
            c.message, c.status, c.reply or "",
            c.created_at.isoformat() if c.created_at else "",
        ])

    output.seek(0)

    filename = f"contacts_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/audit-logs", response_model=APIResponse)
async def get_audit_logs(
    request: Request,
    audit_service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
):
    """获取审计日志（需要认证）"""
    logs = await audit_service.get_recent()
    return APIResponse(data=[
        {
            "id": log.id,
            "username": log.username,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "detail": log.detail,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ])
