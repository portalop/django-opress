from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse
from subdomains.utils import reverse as s_reverse


def delete_cache(url, subdominio=None):
    if url[:4] == 'http':
        url = url.replace('http://', '').replace('https://', '')
        url = url[url.find('/'):]
        cache.delete('%s-%s' % (subdominio, url))
    else:
        cache.delete('-%s' % url)


@receiver(post_save)
def clear_cache(sender, instance, **kwargs):
    try:
        if sender.__name__ == 'Articulo':
            subdominio = instance.blog.subdominio
        elif sender.__name__ == 'Blog':
            subdominio = instance.subdominio
        else:
            subdominio = None
        delete_cache(instance.get_absolute_url(), subdominio)
    except AttributeError:
        pass
    for update_cache in settings.OPRESS_CACHE_UPDATE:
        if sender.__name__ in update_cache['modelos']:
            for vista in update_cache['vistas']:
                delete_cache(reverse(vista))
    if sender.__name__ in ('Noticia', 'Agenda', 'AgendaFechaExcluida', 'Destacado', 'Documento', 'CategoriaDocumento', 'Articulo'):
        delete_cache(reverse('opress:index'))
    if sender.__name__ == 'Pagina':
        if instance.url:
            delete_cache(instance.get_absolute_url())
        # else:
        #     post_save.disconnect(clear_cache, sender=Pagina)
        #     instance.tiene_menu_bloque = instance.es_microsite()
        #     instance.url = instance.get_url()
        #     instance.save()
        #     post_save.connect(clear_cache, sender=Pagina)
    if sender.__name__ == 'Noticia':
        delete_cache(reverse('opress:news'))
    if sender.__name__ in ('Agenda', 'AgendaFechaExcluida'):
        delete_cache(reverse('opress:events'))
    if sender.__name__ == 'Bloque':
        if instance.noticia:
            delete_cache(instance.noticia.get_absolute_url())
        for pagina in instance.get_paginas():
            delete_cache(pagina.get_absolute_url())
    if sender.__name__ == 'Documento' or sender.__name__ == 'CategoriaDocumento':
        delete_cache(reverse('opress:documents'))
    if sender.__name__ == 'Articulo':
        delete_cache(s_reverse('blog_index', subdomain=instance.blog.subdominio), subdominio=instance.blog.subdominio)
        delete_cache(s_reverse('blog_rss', subdomain=instance.blog.subdominio), subdominio=instance.blog.subdominio)
    if sender.__name__ in ('Comment', 'FluentComment'):
        delete_cache(instance.content_object.get_absolute_url(), subdominio=instance.content_object.blog.subdominio)
        delete_cache(s_reverse('blog_index', subdomain=instance.content_object.blog.subdominio), subdominio=instance.content_object.blog.subdominio)
