import logging
import os

from celery import Celery
from flask import url_for
from flask_mail import Message

from myApp import mail, create_app

celery = Celery(__name__, broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"))
logger = logging.getLogger(__name__)

@celery.task
def _send_async_email(subject: str, recipient: str, body: str) -> None:
    app = create_app()
    with app.app_context():
        try:
            sender = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
            msg = Message(subject, sender=sender, recipients=[recipient])
            msg.body = body
            mail.send(msg)
        except Exception:
            logger.exception("Failed to send email")

def send_password_reset_email(email: str, token: str) -> None:
    reset_link = url_for('users.reset_token', token=token, _external=True)
    body = f"""To reset your password, visit the following link:
{reset_link}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    try:
        _send_async_email.delay('Password Reset Request', email, body)
    except Exception:
        logger.exception("Failed to queue password reset email")
