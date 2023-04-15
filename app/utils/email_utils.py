from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List
from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.email_username,
    MAIL_PASSWORD=settings.email_password,
    MAIL_FROM=settings.email_from,
    MAIL_PORT=settings.email_smtp_port,
    MAIL_SERVER=settings.email_smtp_server,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_email(to: List[EmailStr], subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=to,
        body=body,
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(message)