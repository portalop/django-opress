from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings
from photologue.models import Photo, PhotoSize
from photologue.fields import PhotoField
from mptt.models import MPTTModel, TreeForeignKey

PAGES_ICON_SIZE_LABEL = getattr(settings, 'OPRESS_PAGES_ICON_SIZE_LABEL', '(110x110px)')
PAGES_ICON_SIZE = getattr(settings, 'OPRESS_PAGES_ICON_SIZE', 'page_icon')

@python_2_unicode_compatible
class Pagina(MPTTModel):
    titulo = models.CharField("Título", max_length=300)
    slug = models.SlugField('url', unique=True)
    icono = PhotoField(image_size="page_icon", verbose_name="Icono " + PAGES_ICON_SIZE_LABEL, blank=True, null=True, on_delete=models.SET_NULL, related_name='paginas_iconos_set')
    parent = TreeForeignKey('self', verbose_name="Pertenece a", null=True, blank=True, related_name='children')
    descripcion = models.TextField("Descripción", blank=True)
    contenido = models.TextField(blank=True)
    in_menu = models.BooleanField("¿Está en el menú?", default=False)
    menu = models.CharField("Menú", blank=True, max_length=300)
    imagen_cabecera = PhotoField(image_size="page_icon", verbose_name="Imagen cabecera " + PAGES_ICON_SIZE_LABEL, blank=True, null=True, on_delete=models.SET_NULL, related_name='paginas_cabeceras_set')
    template_url = models.CharField("URL Plantilla", blank=True, max_length=300)
    es_seccion = models.BooleanField("¿Es sección?", default=False)
    def __str__(self):
        return self.titulo
    class Meta:
        verbose_name = 'página'
        verbose_name_plural = 'páginas'
        ordering = ['titulo']
        order_with_respect_to = 'parent'
    class MPTTMeta:
        order_insertion_by = ['titulo']
