import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from api.email import CustomPasswordResetEmail

logger = logging.getLogger('tasks')


@shared_task
def send_reset_password_email(user_id: int, data: dict):
    """Отправка письма о смене пароля."""

    email = data.get('email')
    email_list = [email,]
    user = get_user_model().objects.get(id=user_id)
    CustomPasswordResetEmail(email=email, user=user).send(email_list)
    logger.info(
        'Письмо смены пароля отправлено.'
    )
