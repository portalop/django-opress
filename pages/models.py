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
    icono = PhotoField(image_size="page_icon", verbose_name="Icono " + PAGES_ICON_SIZE_LABEL, blank=True, null=True)
    parent = TreeForeignKey('self', verbose_name="Pertenece a", null=True, blank=True, related_name='children')
    def __str__(self):
        return self.titulo
    def page_icon(self):
        if self.icono:
            return u'<img src="%s" />' % getattr(self.icono, "get_%s_url" % PAGES_ICON_SIZE)()
        else:
            return "<em>(Sin icono)</em>"
    page_icon.short_description = 'Vista previa icono'
    page_icon.allow_tags = True
    class Meta:
        verbose_name = 'página'
        verbose_name_plural = 'páginas'
        ordering = ['titulo']
    class MPTTMeta:
        order_insertion_by = ['titulo']
