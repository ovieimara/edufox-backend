from django.apps import AppConfig


class AutocompleteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'autocomplete'

    def ready(self):
        # Start the scheduler when the app is ready
        from . import scheduler

        # scheduler.start()

    def stop(self):
        from . import scheduler

        # Stop the scheduler when the app is stopped
        scheduler.shutdown()
