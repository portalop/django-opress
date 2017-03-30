# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from subdomains.utils import reverse as s_reverse
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as _date
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from django.utils import timezone
from datetime import datetime
from photologue.fields import PhotoField
from filebrowser.fields import FileBrowseField
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from sortedm2m.fields import SortedManyToManyField
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase, CommonGenericTaggedItemBase, TaggedItemBase


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
    'noticias_icono_portada': ('noticias_icono_portada', '140x140px'),
    'noticia_imagen': ('noticia_imagen', '994x350px'),
    'noticias_relacionadas': ('noticias_relacionadas', '190x190px'),
    'agenda_icono': ('agenda_icono', '100x100px'),
    'agenda_imagen': ('agenda_imagen', '730x300px'),
    'portada_destacado': ('portada_destacado', '1040x356px'),
    'autor_foto': ('autor_foto', '90x90px'),
    'prensa_icono': ('prensa_icono', '200x120px'),
    'documento_icono': ('documento_icono', '300x187px'),
    'bloque_icono': ('bloque_icono', '300x187px'),
    'blog_articulo_icono': ('blog_articulo_icono', '330x207px'),
    'autor_blog_foto': ('autor_blog_foto', '330x207px'),
    'autor_articulo_foto': ('autor_articulo_foto', '330x207px'),
    'recurso_icono': ('recurso_icono', '140x140px'),
    'blog_imagen': ('blog_imagen', u'360x240px'),
    'otro_blog_imagen': ('otro_blog_imagen', u'152x140px'),
})
MENU_MAX_LEVEL = getattr(settings, 'OPRESS_MENU_MAX_LEVEL', 0)

BLOCK_TYPE_CHOICES = (
    ('', _('-- Seleccione un tipo de bloque --')),
    ('html', _('Contenido libre (HTML)')),
    ('image', _('Imagen')),
    ('card', _('Ficha (imagen + HTML)')),
    ('timeline', _('Timeline')),
    ('flickr', _('Álbum de Flickr')),
    ('youtube', _('Vídeo de youtube')),
    ('map', _('Mapa de Google')),
)
TIMELINE_ORIENTATION_CHOICES = (
    ('horizontal', _('Horizontal')),
    ('vertical', _('Vertical')),
)

GMAP_TYPE_CHOICES = (
    ('m', _('Mapa')),
    ('k', _('Satélite')),
    ('h', _('Híbrido')),
    ('p', _('Terreno')),
    ('e', _('Google Earth')),
)

MESSAGE_TYPE_CHOICES = (
    ('', _('-- Elija una de la lista --')),
    ('general', _('Información general')),
    ('vocacional', _('Vocacional')),
    ('webmaster', _('Sobre la página web')),
)

BLOG_TYPE_CHOICES = (
    (1, _('Blogs en dominicos.org')),
    (2, _('Blogs en páginas dominicanas')),
    (3, _('Otros blogs')),
)

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
SIGLAS_SEMANA = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
MESES_ANYO = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

RESOURCE_TYPE_CHOICES = (
    ('', _('-- Seleccione un tipo de recurso --')),
    #('formación', _('Formación (URL)')),
    ('vídeo', _('Vídeo (Youtube)')),
    ('audio', _('Audio (Soundcloud)')),
    ('libro', _('Libro (URL)')),
    ('resena', _('Reseña de libro')),
    ('documento', _('Documento (URL)')),
)

class HierarchicalTag (MPTTModel, TagBase):
    parent = TreeForeignKey('self', verbose_name="Pertenece a", null=True, blank=True, related_name='children')
    class Meta:
        verbose_name = 'etiqueta'
        order_with_respect_to = 'parent'
    class MPTTMeta:
        order_insertion_by = ['name']

class TaggedContentItem (CommonGenericTaggedItemBase):
    tag = models.ForeignKey('HierarchicalTag', related_name='tags')
    #content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    #content_object = fields.GenericForeignKey('content_type', 'object_id')

class Sitio(Site):
    db = models.CharField(max_length=100, null=True, blank=True)
    token = models.CharField(max_length=100, null=True, blank=True)

class MenuManager(TreeManager):
    def get_menu(self):
        return super(MenuManager, self).get_queryset().filter(in_menu=True, level__lte=MENU_MAX_LEVEL)

class LocationTag(TagBase):

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"

class LocationTags(GenericTaggedItemBase):
    tag = models.ForeignKey(LocationTag)

@python_2_unicode_compatible
class Pagina(MPTTModel):
    titulo = models.CharField("Título", max_length=100)
    slug = models.SlugField('url', unique=False, max_length=250)
    icono = PhotoField(image_size=IMAGE_SIZES['pagina_icono'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['pagina_icono'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='paginas_iconos_set')
    parent = TreeForeignKey('self', verbose_name="Pertenece a", null=True, blank=True, related_name='children')
    descripcion = models.TextField("Descripción", blank=True)
    #tags = TaggableManager('Etiquetas', blank=True)
    tags = TaggableManager('Etiquetas', through=TaggedContentItem, blank=True)
    contenido = models.TextField(blank=True)
    in_menu = models.BooleanField("¿Está en el menú?", default=True)
    menu = models.CharField("Menú", blank=True, max_length=300)
    imagen_cabecera = PhotoField(image_size=IMAGE_SIZES['pagina_cabecera'][IMAGESIZE_NAME], verbose_name="Imagen cabecera " + IMAGE_SIZES['pagina_cabecera'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='paginas_cabeceras_set')
    template_url = models.CharField("URL Plantilla", blank=True, max_length=300)
    es_seccion = models.BooleanField("¿Es sección?", default=False)
    url = models.CharField("Url", max_length=1000, default='')
    tiene_menu_bloque = models.BooleanField("¿Tiene bloque de menú?", default=False)
    head_title = models.CharField("Título para SEO", max_length=200, null=True, blank=True)
    meta_description = models.CharField("META description para SEO", max_length=300, null=True, blank=True)

    objects = MenuManager()
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    def get_absolute_url(self):
        return reverse('opress:static_page', args=[self.get_url()])
    def get_url(self):
        url_ancestors = ''
        for ancestor in self.get_ancestors():
            if ancestor.es_seccion:
                url_ancestors += ancestor.slug + '/'
        return url_ancestors + self.slug
    def es_microsite(self):
        return Bloque.objects.filter(se_hereda=True, paginas_cabecera__in=(self.get_ancestors(include_self=True))).exists()
    def get_template(self):
        if self.template_url:
            return self.template_url
        else:
            if self.parent:
                return self.parent.get_template()
            else:
                return None
    def get_imagen_cabecera_seccion(self):
        if self.imagen_cabecera:
            return self.imagen_cabecera
        else:
            if self.parent:
                return self.parent.get_imagen_cabecera_seccion()
            else:
                return None
    # def save(self):
    #     super(Pagina, self).save()
    #     self.tiene_menu_bloque = self.es_microsite()
    #     self.url = self.get_url()
    #     super(Pagina, self).save()
    def __str__(self):
        return self.menu or self.titulo or 'Sin título'
    class Meta:
        verbose_name = 'página'
        verbose_name_plural = 'páginas'
        #ordering = ['titulo']
        order_with_respect_to = 'parent'
    class MPTTMeta:
        order_insertion_by = ['titulo']

@python_2_unicode_compatible
class Noticia(models.Model):
    titulo = models.CharField("Título", max_length=300)
    slug = models.SlugField('url', unique=True)
    fecha = models.DateField('Fecha', default=datetime.now, blank=True, db_index=True)
    entradilla = models.TextField('Entradilla')
    icono = PhotoField(image_size=IMAGE_SIZES['noticias_relacionadas'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['noticias_relacionadas'][IMAGESIZE_LABEL], on_delete=models.PROTECT, related_name='noticias_iconos_set')
    imagen = PhotoField(image_size=IMAGE_SIZES['noticia_imagen'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['noticia_imagen'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.PROTECT, related_name='noticias_imagenes_set')
    #tags = TaggableManager('Etiquetas', blank=True)
    tags = TaggableManager('Etiquetas', through=TaggedContentItem, blank=True)
    contenido = models.TextField('Contenido')
    def get_absolute_url(self):
        return reverse('opress:news_detail', args=[self.slug])
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
    fecha_fin = models.DateField('Fecha de fin', db_index=True)
    entradilla = models.TextField('Entradilla', null=True, blank=True)
    icono = PhotoField(image_size=IMAGE_SIZES['agenda_icono'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['agenda_icono'][IMAGESIZE_LABEL], on_delete=models.PROTECT, blank=True, null=True, related_name='agenda_iconos_set')
    imagen = PhotoField(image_size=IMAGE_SIZES['agenda_imagen'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['agenda_imagen'][IMAGESIZE_LABEL], on_delete=models.PROTECT, blank=True, null=True, related_name='agenda_imagenes_set')
    #tags = TaggableManager('Etiquetas', blank=True)
    tags = TaggableManager('Etiquetas', through=TaggedContentItem, blank=True)
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
    fecha_publicacion = models.DateField('Fecha de publicación', default=datetime.now, blank=True, db_index=True)
    localidad = TaggableManager('Localidad', blank=True, through=LocationTags)
    def get_absolute_url(self):
        return reverse('opress:event_detail', args=[self.slug])
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
    def get_days(self):
        return (self.fecha_fin - self.fecha_inicio).days
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
    icono = PhotoField(image_size=IMAGE_SIZES['bloque_icono'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['bloque_icono'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='bloques_iconos_set')
    youtube_id = models.CharField("Id o url del vídeo (Youtube)", max_length=500, blank=True, null=True)
    timeline = models.ForeignKey('Timeline', verbose_name=_('Timeline'), null=True, blank=True)
    mapa = models.ForeignKey('PuntoGoogleMap', verbose_name=_('Mapa de Google'), null=True, blank=True)
    se_hereda = models.BooleanField(default=False)
    grupo = models.CharField(max_length=100, null=True, blank=True)
    def get_paginas(self):
        paginas_list = []
        if self.paginas_cabecera:
            paginas_list += self.paginas_cabecera
        if self.paginas_pie:
            paginas_list += self.paginas_pie
        if self.se_hereda:
            for pagina in paginas_list:
                paginas_list = paginas_list | pagina.get_descendants(include_self==False)
        return paginas_list
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
    visible = models.BooleanField("Visible en la portada", default=True)
    pagina = models.ManyToManyField(Pagina, verbose_name="Páginas en que se muestra")
    fecha = models.DateField('Fecha de publicación', blank=True, null=True)
    seccion = models.CharField("Sección", max_length=100, null=True, blank=True)
    ventana_nueva = models.BooleanField("Se abre en ventana nueva", default=True)
    def __str__(self):
        return self.titulo
    class Meta:
        ordering = ['titulo']

@python_2_unicode_compatible
class CategoriaDocumento(MPTTModel):
    nombre = models.CharField("Nombre", max_length=300)
    slug = models.SlugField('url', unique=False)
    parent = TreeForeignKey('self', verbose_name="Pertenece a", null=True, blank=True, related_name='children')
    pagina = TreeForeignKey(Pagina, verbose_name="Página asociada", null=True, blank=True)
    def __str__(self):
        return self.nombre
    def get_absolute_url(self):
        return reverse('opress:documents_archive', args=[self.get_url()])
    def get_url(self):
        url_ancestors = ''
        for ancestor in self.get_ancestors():
            url_ancestors += ancestor.slug + '/'
        return url_ancestors + self.slug
    class Meta:
        verbose_name = 'categoría de documentos'
        verbose_name_plural = 'categorías de documentos'
        order_with_respect_to = 'parent'

@python_2_unicode_compatible
class Documento(models.Model):
    nombre = models.CharField("Nombre", max_length=300)
    slug = models.SlugField('url', unique=False)
    descripcion = models.TextField('Entradilla', null=True, blank=True)
    fecha = models.DateField('Fecha', default=datetime.now, blank=True)
    archivo = FileBrowseField("Archivo PDF", max_length=300, extensions=settings.FILEBROWSER_EXTENSIONS["Document"], blank=True, null=True)
    scribd_id =  models.CharField("ID de Scribd", max_length=30, blank=True, null=True)
    icono = PhotoField(image_size=IMAGE_SIZES['documento_icono'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['documento_icono'][IMAGESIZE_LABEL], on_delete=models.SET_NULL, blank=True, null=True)
    contenido = models.TextField(blank=True, null=True)
    categoria = TreeForeignKey(CategoriaDocumento, verbose_name=_('Categoría'), blank=True, null=True)
    def __str__(self):
        return self.nombre
    def get_absolute_url(self):
        return reverse('opress:document_detail', args=[self.get_url()])
    def get_url(self):
        return self.categoria.get_url() + '/' + self.slug
    class Meta:
        order_with_respect_to = 'categoria'

@python_2_unicode_compatible
class Boletin(models.Model):
    nombre = models.CharField("Nombre", max_length=300)
    fecha_inicio = models.DateField('Fecha de inicio', db_index=True)
    fecha_fin = models.DateField('Fecha de fin', null=True, blank=True, db_index=True, default=timezone.now)
    imagen = PhotoField(image_size=IMAGE_SIZES['portada_destacado'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['portada_destacado'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL)
    cabecera = models.TextField(blank=True)
    pie = models.TextField(blank=True)
    def __str__(self):
        return self.nombre
    def ver_boletin(self):
        return "<a target='_blank' href='%s'>Generar boletín</a>" % reverse("opress:generar_boletin", args=(self.id,))
    ver_boletin.short_description = 'Generar'
    ver_boletin.allow_tags = True
    class Meta:
        verbose_name = 'boletín'
        verbose_name_plural = 'boletines'
        ordering = ['fecha_inicio']

@python_2_unicode_compatible
class TipoMensaje(models.Model):
    nombre = models.CharField(_('Nombre'), max_length=300)
    destinatario = models.EmailField("Correo electrónico destinatario", max_length=254)
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'tipo de mensaje'
        verbose_name_plural = 'tipos de mensaje'

@python_2_unicode_compatible
class Mensaje(models.Model):
    remitente = models.EmailField("Correo electrónico", max_length=254)
    fecha = models.DateTimeField('Fecha', default=datetime.now)
    tipo = models.ForeignKey(TipoMensaje, verbose_name=_('Tipo de mensaje'), blank=True, null=True)
    texto = models.TextField()
    destinatario = models.CharField("Destinatario", max_length=300)
    ip_origen = models.CharField("IP de origen", max_length=100, null=True)
    def __str__(self):
        return self.remitente

@python_2_unicode_compatible
class GoogleMap(models.Model):
    nombre = models.CharField("Nombre", max_length=300)
    codigo = models.CharField("Identificador", max_length=300)
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'mapa de Google'
        verbose_name_plural = 'mapas de Google'

@python_2_unicode_compatible
class PuntoGoogleMap(models.Model):
    nombre = models.CharField("Nombre", max_length=300)
    enlace = models.CharField("Enlace", max_length=2000)
    mapa = models.ForeignKey('GoogleMap', verbose_name=_('Mapa'), null=True, blank=True)
    tipo = models.CharField(_('Tipo de mapa'), max_length=1, choices=GMAP_TYPE_CHOICES, default="m")
    def __str__(self):
        return self.nombre
    def get_url(self):
        query_string = self.enlace.split("?")[1].split("&")
        url = "https://www.google.com/maps/d/embed?mid=" + self.mapa.codigo + "&source=embed&hl=es&geocode=&ie=UTF8&hq&msa=0&output=embed&t=" + self.tipo
        for parametro in query_string:
            if parametro.split("=")[0] == "ll" or parametro.split("=")[0] == "spn" or parametro.split("=")[0] == "z" or parametro.split("=")[0] == "iwloc":
                url += "&" + parametro
        return url
    class Meta:
        verbose_name = 'punto en mapa de Google'
        verbose_name_plural = 'puntos en mapa de Google'

@python_2_unicode_compatible
class PublicacionSitio(models.Model):
    limit = models.Q(app_label='opress', model='noticia') | \
        models.Q(app_label='opress', model='agenda')
    content_type = models.ForeignKey(ContentType, verbose_name=_('tipo de contenido'), limit_choices_to=limit)
    object_id = models.PositiveIntegerField(verbose_name=_('contenido relacionado'))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    content_object.short_description = 'Contenido a publicar'
    content_object.admin_order_field = 'object_id'
    sitio = models.ForeignKey('Sitio', verbose_name=_('Sitio para publicar'))
    def __str__(self):
        return "[%s] [%s] %s" % (self.content_type, self.content_object, self.sitio)

@python_2_unicode_compatible
class Autor(models.Model):
    nombre = models.CharField(_('Nombre y apellidos'), max_length=300)
    def __str__(self):
        return nombre
    class Meta:
        abstract = True

@python_2_unicode_compatible
class AutorBlog(Autor):
    email = models.EmailField(_('Correo electrónico'),)
    curriculum = models.TextField(_('Currículum'), blank=True)
    foto = PhotoField(image_size=IMAGE_SIZES['blog_imagen'][IMAGESIZE_NAME], verbose_name="Foto " + IMAGE_SIZES['blog_imagen'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='%(class)s_fotos_set')
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'autor de blog'
        verbose_name_plural = 'autores de blogs'
        ordering = ['nombre']

@python_2_unicode_compatible
class AutorArticulo(Autor):
    lugar = models.CharField("Lugar", max_length=300, blank=True, null=True)
    foto = PhotoField(image_size=IMAGE_SIZES['autor_articulo_foto'][IMAGESIZE_NAME], verbose_name="Foto " + IMAGE_SIZES['autor_articulo_foto'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='%(class)s_fotos_set')
    def __str__(self):
        return self.nombre

@python_2_unicode_compatible
class Blog(models.Model):
    titulo = models.CharField(_('Título'), max_length=300)
    autor = models.ForeignKey(AutorBlog, verbose_name=_('Autor'))
    usuario = models.ForeignKey(User, verbose_name=_('Usuario del Kit'), null=True, blank=True)
    subtitulo = models.TextField(_('Subtítulo'), null=True, blank=True)
    descripcion = models.TextField(_('Descripción'), null=True, blank=True)
    url = models.CharField(max_length=500)
    codigo_urchin = models.CharField(_('Código Urchin'), null=True, blank=True, max_length=30)
    tiene_categorias = models.BooleanField("¿Tiene categorías?", default=False)
    es_colectivo = models.BooleanField("¿Es colectivo?", default=False)
    multiidioma = models.BooleanField("¿Es multiidioma?", default=False)
    tiene_destacados = models.BooleanField("¿Tiene destacados?", default=False)
    gplus_profile = models.CharField("Enlace al perfil de Google+", max_length=500, null=True, blank=True)
    subdominio = models.CharField(max_length=500)
    imagen = PhotoField(image_size=IMAGE_SIZES['blog_imagen'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['blog_imagen'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='%(class)s_imagenes_set')
    def get_absolute_url(self):
        return s_reverse ('blog_index', subdomain=self.subdominio)
    def imagen_img(self):
        if self.imagen:
            return u'<img src="%s?%s" />' % (self.imagen.get_admin_thumbnail_url(), datetime.now().time().microsecond)
        else:
            return "<em>(Sin imagen)</em>"
    imagen_img.short_description = 'Imagen'
    imagen_img.allow_tags = True
    def __str__(self):
        return self.titulo
    class Meta:
        permissions = (
            ('admin_blogs', 'Can manage all blogs'),
        )

@python_2_unicode_compatible
class SeccionBlog(models.Model):
    blog = models.ForeignKey(Blog, verbose_name=_('Blog'))
    nombre = models.CharField("Nombre", max_length=300)
    slug = models.SlugField('url', unique=False)
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'sección de blog'
        verbose_name_plural = 'secciones de blogs'
        ordering = ['nombre']

@python_2_unicode_compatible
class OtroBlog(models.Model):
    titulo = models.CharField(_('Título'), max_length=300)
    autor = models.CharField(_('Autor'), max_length=300)
    tipo = tipo = models.PositiveIntegerField(_('Tipo de blog'), choices=BLOG_TYPE_CHOICES)
    blog = models.ForeignKey(Blog, verbose_name=_('Blog'), blank=True, null=True)
    descripcion = models.TextField(_('Descripción'), null=True, blank=True)
    url = models.CharField(max_length=500)
    imagen = PhotoField(image_size=IMAGE_SIZES['otro_blog_imagen'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['otro_blog_imagen'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='%(class)s_imagenes_set')
    rss = models.CharField(max_length=500, blank=True, null=True)
    suscripcion_correo = models.CharField(max_length=1000, blank=True, null=True)
    def imagen_img(self):
        if self.imagen:
            return u'<img src="%s?%s" />' % (self.imagen.get_admin_thumbnail_url(), datetime.now().time().microsecond)
        else:
            return "<em>(Sin imagen)</em>"
    imagen_img.short_description = 'Imagen'
    imagen_img.allow_tags = True
    def __str__(self):
        return self.titulo

@python_2_unicode_compatible
class OtroArticulo(models.Model):
    blog = models.ForeignKey(OtroBlog, verbose_name=_('Blog'))
    titulo = models.CharField(_('Título'), max_length=300)
    subtitulo = models.CharField(_('Subtítulo'), max_length=3000, null=True, blank=True)
    autor = models.CharField(_('Autor'), max_length=300, null=True, blank=True)
    fecha = models.DateField('Fecha', null=True)
    url = models.CharField(max_length=500)
    guid = models.CharField(max_length=500)
    imagen = models.CharField("Imagen (URL)", max_length=500, blank=True, null=True)
    descripcion = models.TextField(_('Descripción'), null=True, blank=True)
    def __str__(self):
        return '[%s] %s' % (self.blog.titulo, self.titulo)

@python_2_unicode_compatible
class Articulo(models.Model):
    blog = models.ForeignKey(Blog, verbose_name=_('Blog'))
    titulo = models.CharField(_('Título'), max_length=300)
    slug = models.SlugField('url', unique=False)
    subtitulo = models.CharField(_('Subtítulo'), max_length=3000, blank=True, null=True)
    autor = models.ForeignKey(AutorArticulo, verbose_name=_('Autor'), blank=True, null=True)
    icono = PhotoField(image_size=IMAGE_SIZES['blog_imagen'][IMAGESIZE_NAME], verbose_name="Imagen " + IMAGE_SIZES['blog_imagen'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL, related_name='articulos_iconos_set')
    contenido = models.TextField(_('Contenido'))
    fecha = models.DateField('Fecha', default=datetime.now, db_index=True)
    inicio = models.DateField('Fecha de publicación', blank=True, null=True, db_index=True)
    seccion = models.ForeignKey(SeccionBlog, verbose_name=_('Sección'), blank=True, null=True)
    es_portada = models.BooleanField("¿Aparece en la portada?", default=False)
    es_destacado = models.BooleanField("¿Hay que destacarlo?", default=False)
    def get_absolute_url(self):
        return s_reverse('blog_article', subdomain=self.blog.subdominio, kwargs={'section': self.seccion.slug if self.seccion else 'articulos', 'slug': self.slug})
    def __str__(self):
        return '[%s] %s' % (self.blog.titulo, self.titulo)
    class Meta:
        verbose_name = 'Artículo'

@python_2_unicode_compatible
class AparicionPrensa(models.Model):
    fecha = models.DateField('Fecha', db_index=True, default=timezone.now)
    titulo = models.CharField("Título", max_length=300)
    medio = models.CharField("Medio", max_length=300)
    enlace = models.CharField("Enlace (URL)", max_length=500, blank=True, null=True)
    archivo = FileBrowseField("Archivo PDF", max_length=300, extensions=settings.FILEBROWSER_EXTENSIONS["Document"], blank=True, null=True)
    icono = PhotoField(image_size=IMAGE_SIZES['prensa_icono'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['prensa_icono'][IMAGESIZE_LABEL], blank=True, null=True, on_delete=models.SET_NULL)
    descripcion = models.TextField(_('Descripción'), null=True, blank=True)
    pagina = models.ManyToManyField(Pagina, verbose_name="Páginas en que se muestra", blank=True)
    def __str__(self):
        return self.titulo
    class Meta:
        ordering = ['fecha']
        verbose_name = 'aparición en prensa'
        verbose_name_plural = 'apariciones en prensa'

@python_2_unicode_compatible
class ProveedorMultimedia(models.Model):
    nombre = models.CharField("Nombre", max_length=100)
    identificador = models.CharField("Identificador (ID)", max_length=500, blank=True, null=True)
    clave = models.CharField("Clave de la API", max_length=500, blank=True, null=True)
    tipo = models.CharField("Tipo", max_length=100)
    slug = models.SlugField("Slug", unique=True)
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'proveedor de contenidos multimedia'
        verbose_name_plural = 'proveedores de contenidos multimedia'

@python_2_unicode_compatible
class Multimedia(models.Model):
    proveedor = models.ForeignKey(ProveedorMultimedia, verbose_name=_('Proveedor de contenidos'))
    fecha = models.DateField('Fecha', db_index=True, default=timezone.now)
    titulo = models.CharField("Título", max_length=300)
    identificador = models.CharField("Identificador (ID)", max_length=500)
    icono = models.CharField("Icono (URL)", max_length=500, blank=True, null=True)
    descripcion = models.TextField(_('Descripción'), null=True, blank=True)
    duracion = models.CharField("Duración", max_length=500, null=True, blank=True)
    es_recurso = models.BooleanField("¿Es recurso?", default=False)
    es_portada = models.BooleanField("¿Aparece en la portada (estudio/verdad)?", default=False)
    tags = TaggableManager('Etiquetas', through=TaggedContentItem, blank=True)
    def icono_img(self):
        if self.icono:
            return u'<img src="%s?%s" />' % (self.icono, datetime.now().time().microsecond)
        else:
            return "<em>(Sin icono)</em>"
    icono_img.short_description = 'Icono'
    icono_img.allow_tags = True
    def get_resource(self):
        self.tipo = self.proveedor.tipo
        return self
    def get_absolute_url(self):
        if self.es_recurso:
            return reverse('opress:recurso_multimedia', kwargs={'mtype': self.proveedor.slug, 'id': self.identificador})
        else:
            return reverse('opress:multimedia_detail', kwargs={'mtype': self.proveedor.slug, 'id': self.identificador})
    def __str__(self):
        return '[%s] %s' % (self.proveedor.nombre, self.titulo)
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'contenido multimedia'
        verbose_name_plural = 'contenidos multimedia'

@python_2_unicode_compatible
class Recurso(models.Model):
    tipo = models.CharField(_('Tipo de recurso'),
                                        max_length=15,
                                        choices=RESOURCE_TYPE_CHOICES)
    fecha = models.DateField('Fecha', db_index=True, default=timezone.now)
    titulo = models.CharField("Título", max_length=300)
    slug = models.SlugField('url', unique=True)
    articulo_blog = models.ForeignKey(Articulo, verbose_name=_('Artículo de blog'), blank=True, null=True)
    multimedia = models.ForeignKey(Multimedia, verbose_name=_('Contenido multimedia'), blank=True, null=True)
    enlace = models.CharField("Enlace (URL)", max_length=500, blank=True, null=True)
    archivo = FileBrowseField("Archivo PDF", max_length=300, extensions=settings.FILEBROWSER_EXTENSIONS["Document"], blank=True, null=True)
    icono = PhotoField(image_size=IMAGE_SIZES['recurso_icono'][IMAGESIZE_NAME], verbose_name="Icono " + IMAGE_SIZES['recurso_icono'][IMAGESIZE_LABEL])
    descripcion = models.TextField(_('Descripción'), null=True, blank=True)
    contenido = models.TextField(_('Contenido'), null=True, blank=True)
    autor = models.CharField(_('Autor'), max_length=300, null=True, blank=True)
    tags = TaggableManager('Etiquetas', through=TaggedContentItem, blank=True)
    es_portada = models.BooleanField("¿Aparece en la portada?", default=False)
    def get_absolute_url(self):
        return reverse('opress:recurso', kwargs={'slug': self.slug})
    def __str__(self):
        return self.titulo
    class Meta:
        ordering = ['fecha']
        verbose_name = 'recurso'
        verbose_name_plural = 'recursos'