from django.apps import AppConfig


class HeadquartersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'headquarters'

    def ready(self):
        import headquarters.signal_handlers
