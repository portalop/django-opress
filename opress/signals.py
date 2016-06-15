from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse
from models import Pagina, Noticia, PublicacionSitio
from serializers import NoticiaSerializer
import requests
import json

@receiver(post_save)
def clear_cache(sender, instance, **kwargs):
    if sender.__name__ in ('Noticia', 'Agenda', 'AgendaFechaExcluida', 'Destacado', 'Pagina', 'Documento', 'CategoriaDocumento'):
        cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, '/'))
        if sender.__name__ in ('Noticia', 'Agenda', 'AgendaFechaExcluida', 'Pagina', 'Documento', 'CategoriaDocumento'):
            if sender.__name__ == 'Pagina':
                if instance.url:
                    cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, instance.get_absolute_url()))
                # else:
                #     post_save.disconnect(clear_cache, sender=Pagina)
                #     instance.tiene_menu_bloque = instance.es_microsite()
                #     instance.url = instance.get_url()
                #     instance.save()
                #     post_save.connect(clear_cache, sender=Pagina)
            if sender.__name__ == 'Noticia':
                cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, reverse('opress.views.news')))
            if sender.__name__ in ('Agenda', 'AgendaFechaExcluida'):
                cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, reverse('opress.views.events')))
            if sender.__name__ == 'Bloque':
                if instance.noticia:
                    cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, instance.noticia.get_absolute_url()))
                for pagina in instance.get_paginas():
                    cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, pagina.get_absolute_url()))
            if sender.__name__ == 'Documento' or sender.__name__ == 'CategoriaDocumento':
                cache.delete('%s-%s' % (settings.CACHE_KEY_PREFIX, reverse('opress.views.documents')))

@receiver(pre_save, sender=PublicacionSitio)
def publish_on_sites(sender, instance, **kwargs):
    if instance.content_type.model == 'noticia':
        headers = {'Authorization': 'Token %s' % instance.sitio.token}
        
        r = requests.post('http://%s%s' % (instance.sitio.domain, reverse('noticia-list')), headers=headers, data=NoticiaSerializer(instance.content_object).data)
#    if sender.__name__ == 'PublicacionSitio':
#        if instance.sitio.db in settings.DATABASES:
#           # contenido = instance.content_object #type.get_object_for_this_type(id=instance.object_id).select_related()
#            contenidos = instance.content_type.model_class().objects.filter(id=instance.object_id).select_related()
#            for contenido in contenidos:
#                contenido.pk = None
#                #links = [rel.get_accessor_name() for rel in contenido._meta.get_all_related_objects()]
#                links = [field for field in contenido._meta.local_fields if field.rel]
#                for link in links:
#                    objects = link.rel.to.objects.filter(pk=getattr(contenido, link.attname))
#                    for object in objects:
#                        #object.pk = None
#                        object.save(using=instance.sitio.db, force_insert=True)
#                contenido.save(using=instance.sitio.db, force_insert=True)