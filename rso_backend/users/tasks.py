from celery import shared_task
from users.models import RSOUser


@shared_task
def reset_membership_fee():
    RSOUser.objects.update(membership_fee=False)