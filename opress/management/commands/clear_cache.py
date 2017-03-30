from django.core.cache import cache
from django.conf import settings
try:
    from django.core.management.base import NoArgsCommand
except ImportError:
    from django.core.management import BaseCommand as NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        cache.clear()
    def handle(self, **options):
        return self.handle_noargs(**options)