"""
留言相关路由 - /api/v1/contacts
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.contact import ContactCreate, ContactReply, ContactResponse, ContactListResponse
from app.schemas.common import APIResponse
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.services.captcha_service import captcha_service
from app.services.audit_service import AuditService
from app.dependencies import get_contact_service, get_email_service, get_audit_service
from app.utils.jwt import get_current_user
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/contacts", tags=["留言"])


@router.get("", response_model=ContactListResponse)
async def list_contacts(
    request: Request,
    contact_service: ContactService = Depends(get_contact_service),
):
    """获取所有留言列表（公开接口，仅展示公开信息）"""
    contacts = await contact_service.get_all()
    return ContactListResponse(
        count=len(contacts),
        contacts=[ContactResponse.model_validate(c) for c in contacts],
    )


@router.post("", response_model=APIResponse)
@limiter.limit("10/minute")
async def create_contact(
    request: Request,
    form: ContactCreate,
    contact_service: ContactService = Depends(get_contact_service),
    email_service: EmailService = Depends(get_email_service),
):
    """提交联系表单（带验证码校验）"""
    # 验证验证码
    error = captcha_service.verify(form.captcha_id, form.captcha_answer)
    if error:
        raise HTTPException(status_code=400, detail=error)

    # 创建留言
    contact = await contact_service.create(form)

    # 异步发送邮件通知（不阻塞响应）
    await email_service.send_notification(
        name=contact.name,
        email=contact.email,
        subject=contact.subject or "",
        message=contact.message,
        contact_id=contact.id,
    )

    return APIResponse(
        message="提交成功！我们会尽快联系您。",
        data={"id": contact.id, "name": contact.name, "email": contact.email},
    )


@router.post("/{contact_id}/reply", response_model=APIResponse)
async def reply_contact(
    request: Request,
    contact_id: int,
    form: ContactReply,
    contact_service: ContactService = Depends(get_contact_service),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
):
    """回复留言（需要认证）"""
    contact = await contact_service.reply(contact_id, form.reply)
    if not contact:
        raise HTTPException(status_code=404, detail="留言不存在")

    # 记录审计日志
    await audit_service.log(
        username=current_user.get("sub", "unknown"),
        action="reply",
        target_type="contact",
        target_id=contact_id,
        ip_address=request.client.host if request.client else None,
    )

    return APIResponse(message="回复成功")


@router.delete("/{contact_id}", response_model=APIResponse)
async def delete_contact(
    request: Request,
    contact_id: int,
    contact_service: ContactService = Depends(get_contact_service),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
):
    """删除留言（需要认证）"""
    deleted = await contact_service.delete(contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="留言不存在")

    # 记录审计日志
    await audit_service.log(
        username=current_user.get("sub", "unknown"),
        action="delete",
        target_type="contact",
        target_id=contact_id,
        ip_address=request.client.host if request.client else None,
    )

    return APIResponse(message="删除成功")
