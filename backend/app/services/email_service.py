"""
异步邮件发送服务（使用 aiosmtplib 替代同步 smtplib）
"""
import os
from typing import Optional
from app.config import settings


class EmailService:
    def __init__(self):
        self.enabled = all([
            settings.SENDER_EMAIL,
            settings.SENDER_PASSWORD,
        ])

    async def send_notification(self, name: str, email: str, subject: str,
                                 message: str, contact_id: int) -> bool:
        """异步发送新留言通知邮件"""
        if not self.enabled:
            print("⚠️ 未配置邮箱，跳过邮件发送")
            return False

        try:
            import aiosmtplib

            recipient = settings.RECIPIENT_EMAIL or settings.SENDER_EMAIL
            email_subject = f"【简历网站】新留言：{name}"
            body = f"""
收到新的联系表单提交：

姓名：{name}
邮箱：{email}
主题：{subject or '无'}
内容：
{message}

编号：{contact_id}
            """.strip()

            message_content = f"Subject: {email_subject}\n\n{body}"

            await aiosmtplib.send(
                message_content,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SENDER_EMAIL,
                password=settings.SENDER_PASSWORD,
                use_tls=True,
            )

            print(f"✅ 邮件发送成功 -> {recipient}")
            return True

        except Exception as e:
            print(f"⚠️ 邮件发送失败：{e}")
            return False

    async def send_reply_notification(self, contact_email: str,
                                       contact_name: str,
                                       reply_text: str) -> bool:
        """异步发送回复通知邮件"""
        if not self.enabled:
            return False

        try:
            import aiosmtplib

            email_subject = f"【简历网站】您收到了一条回复"
            body = f"""
{contact_name}，您好：

您给我们的留言已收到回复：

{reply_text}

感谢您的关注！
            """.strip()

            message_content = f"Subject: {email_subject}\n\n{body}"

            await aiosmtplib.send(
                message_content,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SENDER_EMAIL,
                password=settings.SENDER_PASSWORD,
                use_tls=True,
            )

            print(f"✅ 回复通知邮件已发送 -> {contact_email}")
            return True

        except Exception as e:
            print(f"⚠️ 回复通知邮件发送失败：{e}")
            return False
