from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings
#from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as _date
from datetime import datetime
from photologue.fields import PhotoField
from filebrowser.fields import FileBrowseField
from mptt.models import MPTTModel, TreeForeignKey
from sortedm2m.fields import SortedManyToManyField
from taggit.managers import TaggableManager

PAGES_ICON_SIZE_LABEL = getattr(settings, 'OPRESS_PAGES_ICON_SIZE_LABEL', '(110x110px)')
PAGES_ICON_SIZE = getattr(settings, 'OPRESS_PAGES_ICON_SIZE', 'page_icon')
IMAGESIZE_LABEL = 1
IMAGESIZE_NAME = 0
IMAGE_SIZES = getattr(settings, 'OPRESS_IMAGE_SIZES', {
    'Normal': ('Normal', '400px de ancho'),
    'pagina_icono': ('pagina_icono', '330x207px'),
    'pagina_cabecera': ('pagina_cabecera', '730x300px'),
    'bloque_timeline': ('bloque_timeline', '140x110px'),
    'bloque_ficha': ('bloque_ficha', '430px de ancho'),
    'bloque_ancho_completo': ('bloque_ancho_completo', '730x300px'),
    'noticias_icono_portada': ('noticias_icono_portada', '300x187px'),
    'noticias_icono_ennoticias': ('noticias_icono_ennoticias', '397x250px'),
    'noticia_imagen': ('noticia_imagen', '730x300px'),
    'noticias_relacionadas': ('noticias_relacionadas', '165x103px'),
    'agenda_icono': ('agenda_icono', '90x90px'),
    'portada_destacado': ('portada_destacado', '1040x356px'),
})

BLOCK_TYPE_CHOICES = (
    ('', _('-- Seleccione un tipo de bloque --')),
    ('html', _('Contenido libre (HTML)')),
    ('image', _('Imagen')),
    ('card', _('Ficha (imagen + HTML)')),
    ('timeline', _('Timeline')),
    ('flickr', _('Álbum de Flickr')),
)
TIMELINE_ORIENTATION_CHOICES = (
    ('horizontal', _('Horizontal')),
    ('vertical', _('Vertical')),
)

@python_2_unicode_compatible
class Pagina(MPTTModel):
    titulo = models.CharField("Título", max_length=100)
    slug = models.SlugField('url', unique=False)
    icono = PhotoField(image_size=IMAGE_SIZES['pagina_icono'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['pagina_icono'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='paginas_iconos_set')
    parent = TreeForeignKey('self', verbose_name="Pertenece a", null=True, blank=True, related_name='children')
    descripcion = models.TextField("Descripción", blank=True)
    tags = TaggableManager('Etiquetas', blank=True)
    contenido = models.TextField(blank=True)
    in_menu = models.BooleanField("¿Está en el menú?", default=True)
    menu = models.CharField("Menú", blank=True, max_length=300)
    imagen_cabecera = PhotoField(image_size=IMAGE_SIZES['pagina_cabecera'][IMAGESIZE_NAME], verbose_name="Imagen cabecera " + IMAGE_SIZES['pagina_cabecera'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='paginas_cabeceras_set')
    template_url = models.CharField("URL Plantilla", blank=True, max_length=300)
    es_seccion = models.BooleanField("¿Es sección?", default=False)
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    def get_absolute_url(self):
        return reverse('opress.views.static_page', args=[self.get_url()])
    def get_url(self):
        url_ancestors = ''
        for ancestor in self.get_ancestors():
            if ancestor.es_seccion:
                url_ancestors += ancestor.slug + '/'
        return url_ancestors + self.slug
    def tiene_menu_bloque(self):
        return Bloque.objects.filter(se_hereda=True, paginas_cabecera__in=(self.get_ancestors(include_self=True))).exists()
    def __str__(self):
        return self.menu or self.titulo
    class Meta:
        verbose_name = 'página'
        verbose_name_plural = 'páginas'
        ordering = ['titulo']
        order_with_respect_to = 'parent'
    class MPTTMeta:
        order_insertion_by = ['titulo']

@python_2_unicode_compatible
class Noticia(models.Model):
    titulo = models.CharField("Título", max_length=300)
    slug = models.SlugField('url', unique=True)
    fecha = models.DateField('Fecha', default=datetime.now, blank=True, db_index=True)
    entradilla = models.TextField('Entradilla')
    icono = PhotoField(image_size=IMAGE_SIZES['noticias_icono_portada'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['noticias_icono_portada'][IMAGESIZE_LABEL], on_delete=models.PROTECT, related_name='noticias_iconos_set')
    imagen = PhotoField(image_size=IMAGE_SIZES['noticia_imagen'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['noticia_imagen'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='noticias_imagenes_set')
    tags = TaggableManager('Etiquetas', blank=True)
    contenido = models.TextField('Contenido')
    def get_absolute_url(self):
        return reverse('opress.views.news_detail', args=[self.slug])
    def icono_img(self):
        if self.icono:
            return u'<img src="%s?%s" />' % (self.icono.get_admin_thumbnail_url(), datetime.now().time().microsecond)
        else:
            return "<em>(Sin icono)</em>"
    icono_img.short_description = 'Icono'
    icono_img.allow_tags = True
    def __str__(self):
        return self.titulo
    class Meta:
        ordering = ['-fecha']

@python_2_unicode_compatible
class Agenda(models.Model):
    titulo = models.CharField("Título", max_length=300)
    slug = models.SlugField('url', unique=True)
    fecha_inicio = models.DateField('Fecha de inicio', db_index=True)
    fecha_fin = models.DateField('Fecha de fin', null=True, blank=True, db_index=True)
    entradilla = models.TextField('Entradilla', null=True, blank=True)
    icono = PhotoField(image_size=IMAGE_SIZES['agenda_icono'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['agenda_icono'][IMAGESIZE_LABEL], on_delete=models.SET_NULL, blank=True, null=True)
    tags = TaggableManager('Etiquetas', blank=True)
    contenido = models.TextField('Contenido', null=True, blank=True)
    se_anuncia = models.BooleanField("¿Se anuncia?", default=False)
    inicio_anuncio = models.DateField('Fecha de inicio del anuncio', null=True, blank=True, default=datetime.now)
    fin_anuncio = models.DateField('Fecha de fin del anuncio', null=True, blank=True)
    es_periodico = models.BooleanField("¿Es un evento periódico?", default=False)
    lunes = models.BooleanField(default=False)
    martes = models.BooleanField(default=False)
    miercoles = models.BooleanField(default=False)
    jueves = models.BooleanField(default=False)
    viernes = models.BooleanField(default=False)
    sabado = models.BooleanField(default=False)
    domingo = models.BooleanField(default=False)
    def get_absolute_url(self):
        return reverse('opress.views.event_detail', args=[self.slug])
    def icono_img(self):
        if self.icono:
            return u'<img src="%s?%s" />' % (self.icono.get_admin_thumbnail_url(), datetime.now().time().microsecond)
        else:
            return "<em>(Sin icono)</em>"
    icono_img.short_description = 'Icono'
    icono_img.allow_tags = True
    def get_dates_str(self):
        if self.fecha_inicio == self.fecha_fin:
            return self.fecha_fin.strftime("%-d de " + _date(self.fecha_inicio, "F") + " de %Y")
        else:
            if self.fecha_inicio.month == self.fecha_fin.month:
                return self.fecha_inicio.strftime("Del %-d ") + self.fecha_fin.strftime("al %-d de " + _date(self.fecha_inicio, "F") + " de %Y")
            else:
                return self.fecha_inicio.strftime("Del %-d de " + _date(self.fecha_inicio, "F") + " de %Y ") + self.fecha_fin.strftime("al %-d de " + _date(self.fecha_fin, "F") + " de %Y")
    def __str__(self):
        return self.titulo
    class Meta:
        ordering = ['fecha_inicio']

class AgendaFechaExcluida(models.Model):
    agenda = models.ForeignKey(Agenda, verbose_name=_('Evento'))
    fecha = models.DateField()
    def __str__(self):
        return self.fecha

@python_2_unicode_compatible
class Bloque(models.Model):
    tipo = models.CharField(_('Tipo de bloque'),
                                        max_length=15,
                                        choices=BLOCK_TYPE_CHOICES)
    paginas_cabecera = models.ForeignKey(Pagina,
                                   related_name='bloques_cabecera',
                                   verbose_name=_('Al principio de la página'),
                                   null=True,
                                   blank=True)
    paginas_pie = models.ForeignKey(Pagina,
                                   related_name='bloques_pie',
                                   verbose_name=_('Al final de la página'),
                                   null=True,
                                   blank=True)
    noticia = models.ForeignKey(Noticia,
                                   verbose_name=_('Al final de la noticia'),
                                   null=True,
                                   blank=True)
    titulo = models.CharField("Título", max_length=300, blank=True, null=True)
    imagen = PhotoField(image_size=IMAGE_SIZES['bloque_ancho_completo'][IMAGESIZE_NAME], verbose_name="Banner " + IMAGE_SIZES['bloque_ancho_completo'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='bloques_imagenes_set')
    enlace = models.CharField("Enlace (URL)", max_length=500, blank=True, null=True)
    contenido = models.TextField(blank=True, null=True)
    flickr_user = models.ForeignKey('FlickrUser',
                                   verbose_name=_('Usuario de Flickr'),
                                   null=True,
                                   blank=True)
    flickr_album = models.CharField("Id del álbum (Flickr)", max_length=30, blank=True, null=True)
    timeline = models.ForeignKey('Timeline', verbose_name=_('Timeline'), null=True, blank=True)
    se_hereda = models.BooleanField(default=False)
    def get_paginas(self):
        paginas_list = self.paginas_cabecera.all() | self.paginas_pie.all()
        if self.se_hereda:
            for pagina in paginas_list:
                paginas_list = paginas_list | pagina.get_descendants(include_self==False)
    def get_menu(self):
        if self.se_hereda:
            menu_bloque = self.paginas_cabecera.get_descendants(include_self=True).filter(in_menu=True)
            return menu_bloque
        else:
            return None
    def __str__(self):
        return '[%s] %s' % (self.tipo, self.titulo)
    class Meta:
        verbose_name = 'bloque'
        ordering = ['titulo']

@python_2_unicode_compatible
class FlickrUser(models.Model):
    user_id = models.CharField(_('Identificador (xxxxxxxx@xxx)'),
                                        max_length=20)
    nombre = models.CharField("Nombre", max_length=300)
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'usuario de Flickr'
        verbose_name_plural = 'usuarios de Flickr'
        ordering = ['nombre']

@python_2_unicode_compatible
class Timeline(models.Model):
    nombre = models.CharField("Nombre", max_length=300)
    orientacion = models.CharField(_('Orientación'),
                                        max_length=15,
                                        choices=TIMELINE_ORIENTATION_CHOICES)
    autoplay = models.BooleanField("Autoplay", default=False)
    selected_item = models.ForeignKey('TimelineItem',
                                   verbose_name=_('Fecha seleccionada'),
                                   null=True,
                                   blank=True,
                                   related_name='timeline_selected')
    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ['nombre']

@python_2_unicode_compatible
class TimelineItem(models.Model):
    timeline = models.ForeignKey(Timeline, verbose_name=_('Timeline'))
    fecha = models.CharField("Fecha", max_length=30)
    titulo = models.CharField("Título", max_length=300)
    contenido = models.TextField(blank=True)
    imagen = PhotoField(image_size=IMAGE_SIZES['bloque_timeline'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['bloque_timeline'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.fecha
    class Meta:
        ordering = ['fecha']

@python_2_unicode_compatible
class Destacado(models.Model):
    titulo = models.CharField("Título", max_length=300)
    entradilla = models.TextField(blank=True)
    imagen = PhotoField(image_size=IMAGE_SIZES['portada_destacado'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['portada_destacado'][IMAGESIZE_LABEL], on_delete=models.PROTECT)
    enlace = models.CharField("Enlace (URL)", max_length=500, blank=True, null=True)
    visible = models.BooleanField("Visible", default=True)
    def __str__(self):
        return self.titulo
    class Meta:
        ordering = ['titulo']

@python_2_unicode_compatible
class CategoriaDocumento(MPTTModel):
    nombre = models.CharField("Nombre", max_length=300)
    slug = models.SlugField('url', unique=False)
    parent = TreeForeignKey('self', verbose_name="Pertenece a", null=True, blank=True, related_name='children')
    def __str__(self):
        return self.nombre
    def get_absolute_url(self):
        return reverse('opress.views.documents_archive', args=[self.get_url()])
    def get_url(self):
        url_ancestors = ''
        for ancestor in self.get_ancestors():
            url_ancestors += ancestor.slug + '/'
        return url_ancestors + self.slug
    class Meta:
        verbose_name = 'categoría de documentos'
        verbose_name_plural = 'categorías de documentos'
        ordering = ['nombre']
        order_with_respect_to = 'parent'

@python_2_unicode_compatible
class Documento(models.Model):
    nombre = models.CharField("Nombre", max_length=300)
    slug = models.SlugField('url', unique=False)
    descripcion = models.TextField('Entradilla', null=True, blank=True)
    fecha = models.DateField('Fecha', default=datetime.now, blank=True)
    archivo = FileBrowseField("Archivo PDF", max_length=300, extensions=settings.FILEBROWSER_EXTENSIONS["Document"], blank=True, null=True)
    scribd_id =  models.CharField("ID de Scribd", max_length=30, blank=True, null=True)
    categoria = models.ForeignKey(CategoriaDocumento, verbose_name=_('Categoría'), blank=True, null=True)
    def __str__(self):
        return self.nombre
    def get_absolute_url(self):
        return reverse('opress.views.document_detail', args=[self.get_url()])
    def get_url(self):
        return self.categoria.get_url() + '/' + self.slug
    class Meta:
        ordering = ['nombre']
        order_with_respect_to = 'categoria'

@python_2_unicode_compatible
class Boletin(models.Model):
    nombre = models.CharField("Nombre", max_length=300)
    fecha_inicio = models.DateField('Fecha de inicio', db_index=True)
    fecha_fin = models.DateField('Fecha de fin', null=True, blank=True, db_index=True, default=datetime.today())
    imagen = PhotoField(image_size=IMAGE_SIZES['portada_destacado'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['portada_destacado'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL)
    cabecera = models.TextField(blank=True)
    pie = models.TextField(blank=True)
    def __str__(self):
        return self.nombre
    def ver_boletin(self):
        return "<a target='_blank' href='%s'>Generar boletín</a>" % reverse("generar_boletin", args=(self.id,))
    ver_boletin.short_description = 'Generar'
    ver_boletin.allow_tags = True
    class Meta:
        verbose_name = 'boletín'
        verbose_name_plural = 'boletines'
        ordering = ['fecha_inicio']