from datetime import datetime
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

import aiosmtplib
from jinja2 import Template

from app.core.config import settings


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent.parent / "email-templates" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


async def send_verify_token(to_email: str, token: str):
    confirmation_link = (
        f"{settings.frontend_host}{settings.api_v1_str}/auth/verify/?token={token}"
    )
    message = MIMEMultipart()
    message["From"] = settings.smtp.username
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"

    message.attach(
        MIMEText(
            render_email_template(
                template_name="verify-email.html",
                context={
                    "confirmation_link": confirmation_link,
                    "year": datetime.now().year,
                },
            ),
            "html",
            "utf-8",
        )
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp.host,
        port=settings.smtp.port,
        username=settings.smtp.username,
        password=settings.smtp.password,
        use_tls=True,
    )
