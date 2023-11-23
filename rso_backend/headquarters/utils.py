from datetime import timezone


def unit_upload_path(instance, filename):
    """Путь для сохранения файлов."""
    return (f'units/'
            f'{instance.name}/'
            f'{timezone.now().strftime("%Y/%m/%d")}/'
            f'{filename}')
