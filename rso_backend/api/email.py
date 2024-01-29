import os

from django.conf import settings
from djoser.email import PasswordResetEmail


class CustomPasswordResetEmail(PasswordResetEmail):
    """Кастомный класс отправки письма подтверждения смены пароля.

    Определен класс init для передачи контекста в шаблон письма.
    """

    template_name = os.path.join(
        settings.BASE_DIR, 'templates', 'email', 'password_reset.html'
    )

    def __init__(self, email, user, context=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        site_url = (
            self.context.get('site_url', None)
            if context else settings.DEFAULT_SITE_URL
        )
        self.email = email
        self.user = user
        self.context = {
            'user': self.user,
            'site_name': 'лк.трудкрут.рф',
            'domain': site_url,
            'site_url': site_url,
            'expiration_days': 1,
            'protocol': 'https'
        } if context is None else context
