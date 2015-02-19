from django.apps import AppConfig

class OpressConfig(AppConfig):
    name = 'opress'
    verbose_name = "Opress"

    def ready(self):
        import signals
        super(OpressConfig, self).ready()