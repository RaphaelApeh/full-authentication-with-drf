from typing import Sequence

from django.core import mail
from django.conf import settings


def send_email(subject: str, to: Sequence[str], email_body: str, from_email=settings.DEFAULT_FROM_EMAIL) -> None:

    message = mail.EmailMessage(
        subject,
        email_body,
        from_email,
        to
    )
    message.send()