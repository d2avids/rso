from django.utils import timezone


def user_upload_path(instance, filename):
    """Путь для сохранения файлов."""
    return (f'users/'
            f'{instance.user.username}/'
            f'{timezone.now().strftime("%Y/%m/%d")}/'
            f'{filename}')
