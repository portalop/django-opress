from django.core.cache import cache
from django.conf import settings
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        cache.clear()