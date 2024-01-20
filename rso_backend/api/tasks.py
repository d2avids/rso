import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.email import ActivationEmail
from django.core.mail import send_mail
from users.models import RSOUser
logger = logging.getLogger('tasks')

# @shared_task
# def send_activation_email(*args, **kwargs):
#     print(args, sep='\n')
#     _, context = args
#     # user = context['user']
#     email = ActivationEmail(context=context)
#     return email.send()


# @shared_task
# def send_activation_email(*args, **kwargs):
#     print(args)
#     request, data = args
#     print(request.data)
#     return send_mail(
#         subject='Активация аккаунта',
#         message='Молодец',
#         recipient_list=(request.data['email'], ),
#         fail_silently=False,
#         auth_user=None,
#         auth_password=None,
#         connection=None,
#         html_message=None,
#         from_email=None
#     )

class CustomActivationEmail(ActivationEmail):

    def __call__(self, user, email):
        context = {
            'user': user,
            'site_name': 'RSO',
            'site_url': 'http://127.0.0.1:8080',
            # 'activation_key': self.get_activation_key(user),
            'expiration_days': 1,
        }
        self.send(email, context)

@shared_task
def send_activation_email(id, data):
    user = get_user_model().objects.get(id=id)
    instance = CustomActivationEmail()
    instance(email=data['email'], user=user)
    logger.info(
        'Письмо активации отправлено.'
    )
