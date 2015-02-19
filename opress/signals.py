from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse

@receiver(post_save)
def clear_cache(sender, instance, **kwargs):
    if sender.__name__ in ('Noticia', 'Agenda', 'AgendaFechaExcluida', 'Destacado', 'Pagina'):
        cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, '/'))
        if sender.__name__ in ('Noticia', 'Agenda', 'AgendaFechaExcluida', 'Pagina'):
            cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, instance.get_absolute_url()))
            if sender.__name__ == 'Noticia':
                cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, reverse('opress.views.news')))
            if sender.__name__ in ('Agenda', 'AgendaFechaExcluida'):
                cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, reverse('opress.views.events')))
            if sender.__name__ == 'Bloque':
                if instance.noticia:
                    cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, instance.noticia.get_absolute_url()))
                for pagina in instance.get_paginas():
                    cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, pagina.get_absolute_url()))