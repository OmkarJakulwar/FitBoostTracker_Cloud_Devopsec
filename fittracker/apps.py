from django.apps import AppConfig


class FittrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fittracker'
    
def ready(self):
    import fittracker.signals
