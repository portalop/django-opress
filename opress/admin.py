# -*- coding: utf-8 -*-

import json
import re
import urlparse
import requests
from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.shortcuts import get_object_or_404
from django.forms.models import ModelChoiceField
from django_mptt_admin.admin import DjangoMpttAdmin
from .models import *
from .serializers import NoticiaSerializer, AgendaSerializer
from mptt.forms import TreeNodeMultipleChoiceField
from tinymce.widgets import TinyMCE
from photologue.models import PhotoSize, Photo, Gallery
from photologue.fields import PhotoFormField
from taggit_labels.widgets import LabelWidget
from taggit.forms import TagField


def dimensiones(numero):
    if numero == 0:
        return('proporcional')
    else:
        return('%s px' % numero)


def get_add_link(model):
    return(reverse(
           'admin:%s_%s_add' % (model._meta.app_label, model._meta.object_name.lower()), current_app=admin.site.name))


OPRESS_TINYMCE_DEFAULT_CONFIG = {
    'gallerycon_settings': settings.TINYMCE_DEFAULT_CONFIG['gallerycon_settings']
}


def video_id(value):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    if re.match('^[A-Za-z0-9_-]{11}$', value):
        return value
    query = urlparse.urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if query.path == '/watch' or query.path == '/?#/watch':
            p = urlparse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None


def init_gallerycon_settings():
    OPRESS_TINYMCE_DEFAULT_CONFIG['gallerycon_settings']['sizes'] = []
    OPRESS_TINYMCE_DEFAULT_CONFIG['gallerycon_settings']['links'] = {
        'add_album': get_add_link(Gallery),
        'add_photo': get_add_link(Photo)
    }
    for image_size in PhotoSize.objects.all():
        OPRESS_TINYMCE_DEFAULT_CONFIG['gallerycon_settings']['sizes'].append({'id': image_size.name, 'name': '%(nombre)s (ancho: %(ancho)s, alto: %(alto)s)' % {'nombre': image_size.name, 'ancho': dimensiones(image_size.width), 'alto': dimensiones(image_size.height)}})


def customize_tinyMCE(opciones):
    nueva_config = OPRESS_TINYMCE_DEFAULT_CONFIG.copy()
    nueva_config.update(opciones)
    return nueva_config


class PaginaAdminForm(forms.ModelForm):
    contenido = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))
    tags = TagField(required=False, widget=LabelWidget(model=HierarchicalTag, hierarchical=True))

    def __init__(self, *args, **kwargs):
        request = self.request
        super(PaginaAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()
        if 'parent_id' in request.GET:
            self.fields['parent'].initial = Pagina.objects.get(pk=request.GET.get('parent_id'))


class DestacadoAdminForm(forms.ModelForm):
    pagina = TreeNodeMultipleChoiceField(label="Páginas en que se muestra", required=False, queryset=Pagina.objects.all())


class AparicionPrensaAdminForm(forms.ModelForm):
    pagina = TreeNodeMultipleChoiceField(label="Páginas en que se muestra", required=False, queryset=Pagina.objects.all())


class BloqueAdminForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=BLOCK_TYPE_CHOICES, widget=forms.Select(attrs={"class": "select_block", "onChange": "hide_fields(this)"}))
    contenido = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 300})))

    def __init__(self, *args, **kwargs):
        super(BloqueAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()

    def clean_youtube_id(self):
        data = self.cleaned_data['youtube_id']
        if self.cleaned_data['tipo'] == 'youtube' and not data:
            raise forms.ValidationError(_("Debe especificar un ID o Url de Youtube"))
        if data:
            data = video_id(data)
            if not data:
                raise forms.ValidationError(_(u'El ID o Url de Youtube no es válido'))
        return data

    class Media:
        js = [
            settings.STATIC_URL + 'opress/js/opress.js',
        ]


class NoticiaAdminForm(forms.ModelForm):
    contenido = forms.CharField(widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))
    tags = TagField(required=False, widget=LabelWidget(model=HierarchicalTag, hierarchical=True))

    def __init__(self, *args, **kwargs):
        super(NoticiaAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()


class AgendaAdminForm(forms.ModelForm):
    contenido = forms.CharField(widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))
    tags = TagField(required=False, widget=LabelWidget(model=HierarchicalTag, hierarchical=True))
    localidad = TagField(required=False, widget=LabelWidget(model=LocationTag, hierarchical=False))

    def __init__(self, *args, **kwargs):
        super(AgendaAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()


class CategoriaDocumentoAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = self.request
        super(CategoriaDocumentoAdminForm, self).__init__(*args, **kwargs)
        if 'parent_id' in request.GET:
            self.fields['parent'].initial = CategoriaDocumento.objects.get(pk=request.GET.get('parent_id'))


class DocumentoAdminForm(forms.ModelForm):
    contenido = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 300})))

    def __init__(self, *args, **kwargs):
        super(DocumentoAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()


class BoletinAdminForm(forms.ModelForm):
    cabecera = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))
    pie = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))

    def __init__(self, *args, **kwargs):
        super(BoletinAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()


class RecursoAdminForm(forms.ModelForm):
    descripcion = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 300})))
    contenido = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 800})))
    tags = TagField(required=False, widget=LabelWidget(model=HierarchicalTag, hierarchical=True))

    def __init__(self, *args, **kwargs):
        super(RecursoAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()


class MultimediaAdminForm(forms.ModelForm):
    tags = TagField(required=False, widget=LabelWidget(model=HierarchicalTag, hierarchical=True))


class ArticuloAdminForm(forms.ModelForm):
    contenido = forms.CharField(widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))

    def __init__(self, *args, **kwargs):
        super(ArticuloAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()


class PublicacionSitioInline(GenericTabularInline):
    extra = 1
    model = PublicacionSitio


class StackedInlineWithoutWidgetWrapper(admin.StackedInline):
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        old_formfield = admin.StackedInline.formfield_for_dbfield(self, db_field, **kwargs)
        if (hasattr(old_formfield, 'widget') and
            isinstance(old_formfield.widget, RelatedFieldWidgetWrapper) and
                isinstance(old_formfield, PhotoFormField)):
            old_formfield.widget.can_add_related = False
        return old_formfield


class BloqueCabeceraInline(StackedInlineWithoutWidgetWrapper):
    model = Bloque
    fk_name = 'paginas_cabecera'
    verbose_name = 'bloque de cabecera'
    extra = 1
    exclude = ('paginas_pie', 'noticia')
    form = BloqueAdminForm


class BloquePieInline(StackedInlineWithoutWidgetWrapper):
    model = Bloque
    fk_name = 'paginas_pie'
    verbose_name = 'bloque de pie'
    extra = 1
    exclude = ('paginas_cabecera', 'noticia')
    form = BloqueAdminForm


class PaginaAdmin(DjangoMpttAdmin):
    search_fields = ['titulo', 'descripcion']
    tree_auto_open = 0
    list_display = ('titulo',)
    prepopulated_fields = {'slug': ('titulo',)}
    inlines = [BloqueCabeceraInline, BloquePieInline]
    fieldsets = (
        ('Datos generales', {
            'fields': ('titulo', 'slug', 'icono', 'parent', 'descripcion', 'tags',),
        }),
        ('Cabecera', {
            'classes': ('placeholder bloques_cabecera-group',),
            'fields': ()
        }),
        ('Contenido', {
            'fields': ('contenido',),
        }),
        ('Pie', {
            'classes': ('placeholder bloques_pie-group',),
            'fields': ()
        }),
        ('Configuración avanzada', {
            'fields': (('in_menu', 'menu'), 'imagen_cabecera', 'template_url', 'es_seccion', 'head_title', 'meta_description'),
        })
    )
    form = PaginaAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form_with_request = super(PaginaAdmin, self).get_form(request, obj=None, **kwargs)
        form_with_request.request = request
        return form_with_request

    def save_model(self, request, obj, form, change):
        super(PaginaAdmin, self).save_model(request, obj, form, change)
        obj.tiene_menu_bloque = obj.es_microsite()
        obj.url = obj.get_url()
        obj.save()

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class AutorBlogAdminForm(forms.ModelForm):
    curriculum = forms.CharField(widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))

    def __init__(self, *args, **kwargs):
        super(AutorBlogAdminForm, self).__init__(*args, **kwargs)
        init_gallerycon_settings()


class DestacadoAdmin(admin.ModelAdmin):
    model = Destacado
    form = DestacadoAdminForm


class AparicionPrensaAdmin(admin.ModelAdmin):
    model = AparicionPrensa
    form = AparicionPrensaAdminForm
    list_display = ('fecha', 'titulo', 'medio', 'enlace', 'archivo',)
    list_display_links = ('titulo',)


class BloqueAdmin(admin.ModelAdmin):
    pass


class FlickrUserAdmin(admin.ModelAdmin):
    model = FlickrUser


class TimelineItemAdminForm(forms.ModelForm):
    contenido = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 380, 'height': 300})))


class TimelineItemInline(StackedInlineWithoutWidgetWrapper):
    model = TimelineItem
    extra = 3
    form = TimelineItemAdminForm


class TimelineAdmin(admin.ModelAdmin):
    inlines = [TimelineItemInline]

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class BloqueNoticiaInline(StackedInlineWithoutWidgetWrapper):
    model = Bloque
    verbose_name = 'bloque'
    extra = 1
    exclude = ('paginas_cabecera', 'paginas_pie')
    form = BloqueAdminForm


class NoticiaAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'entradilla', 'fecha']
    list_display = ('icono_img', 'fecha', 'titulo', 'entradilla')
    list_display_links = ('titulo',)
    fields = ('titulo', 'slug', 'fecha', 'entradilla', 'icono', 'imagen', 'tags', 'contenido', 'publicado')
    prepopulated_fields = {'slug': ('titulo',)}
    inlines = [BloqueNoticiaInline, PublicacionSitioInline]
    form = NoticiaAdminForm

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if hasattr(instance, 'sitio'):
                data = NoticiaSerializer(form.instance).data
                url_api = reverse('opress:noticia-list')
                if data['icono']:
                    data['icono']['sites'] = []
                if data['imagen']:
                    data['imagen']['sites'] = []
                for bloque in data['bloques']:
                    if bloque['icono']:
                        bloque['icono']['sites'] = []
                    if bloque['imagen']:
                        bloque['imagen']['sites'] = []
                    if bloque['timeline']:
                        for item in bloque['timeline']['items']:
                            if item['imagen']:
                                item['imagen']['sites'] = []

                to = 'https://' + instance.sitio.domain + url_api
                try:
                    headers = {}
                    headers['Content-Type'] = 'application/json; charset=utf-8'
                    headers['Authorization'] = 'Token ' + instance.sitio.token
                    response = requests.post(to, json.dumps(data), headers=headers, verify=False)
                    response.raise_for_status()
                    instance.content_type = ContentType.objects.get_for_model(form.instance)
                    instance.object_id = form.instance.id
                    instance.content_object = form.instance
                    instance.save()
                except requests.exceptions.HTTPError:
                    # error_message = response.content
                    # raise "Error: " + str(error_message)
                    pass
            else:
                instance.save()
        formset.save_m2m()

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class AgendaAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'entradilla', 'fecha_inicio']
    list_display = ('icono_img', 'fecha_inicio', 'fecha_fin', 'titulo', 'entradilla')
    list_display_links = ('titulo',)
    fields = ('titulo', 'slug', 'fecha_inicio', 'fecha_fin', 'entradilla', 'icono', 'imagen', 'tags', 'contenido', 'publicado', ('se_anuncia', 'inicio_anuncio', 'fin_anuncio',), 'es_periodico', ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'), 'localidad')
    prepopulated_fields = {'slug': ('titulo',), }
    inlines = [PublicacionSitioInline]
    form = AgendaAdminForm

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if hasattr(instance, 'sitio'):
                data = AgendaSerializer(form.instance).data
                url_api = reverse('opress:agenda-list')
                if data['icono']:
                    data['icono']['sites'] = []
                if data['imagen']:
                    data['imagen']['sites'] = []

                to = 'https://' + instance.sitio.domain + url_api
                try:
                    headers = {}
                    headers['Content-Type'] = 'application/json; charset=utf-8'
                    headers['Authorization'] = 'Token ' + instance.sitio.token
                    response = requests.post(to, json.dumps(data), headers=headers, verify=False)
                    response.raise_for_status()
                    instance.content_type = ContentType.objects.get_for_model(form.instance)
                    instance.object_id = form.instance.id
                    instance.content_object = form.instance
                    instance.save()
                except requests.exceptions.HTTPError:
                    # error_message = response.content
                    # raise "Error: " + str(error_message)
                    pass
            else:
                instance.save()
        formset.save_m2m()

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class DocumentoInline(admin.StackedInline):
    inline_classes = ('grp-collapse grp-open',)
    model = Documento
    extra = 0
    form = DocumentoAdminForm


class DocumentoAdmin(admin.ModelAdmin):
    model = Documento
    form = DocumentoAdminForm

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class CategoriaDocumentoAdmin(DjangoMpttAdmin):
    search_fields = ['nombre']
    tree_auto_open = 1
    list_display = ('nombre',)
    inlines = [DocumentoInline]
    form = CategoriaDocumentoAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form_with_request = super(CategoriaDocumentoAdmin, self).get_form(request, obj=None, **kwargs)
        form_with_request.request = request
        return form_with_request


class BoletinAdmin(admin.ModelAdmin):
    search_fields = ['nombre', 'fecha_inicio']
    list_display = ('fecha_inicio', 'fecha_fin', 'nombre', 'ver_boletin')
    list_display_links = ('nombre',)
    fields = ('nombre', 'fecha_inicio', 'fecha_fin', 'imagen', 'cabecera', 'pie')
    form = BoletinAdminForm

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class SitioAdmin(SiteAdmin):
    list_display = ('domain', 'name', 'db')


class IPUserAdmin(admin.ModelAdmin):
    model = IPUser
    list_display = ('user', 'ip_addr', 'publish')


class PublicacionSitioAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'content_object', 'sitio')
    list_display_links = ('content_object',)
    autocomplete_lookup_fields = {
        'generic': [['content_type', 'object_id']],
    }


class MultimediaAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'descripcion', 'fecha']
    list_display = ('proveedor', 'icono_img', 'fecha', 'titulo', 'descripcion', 'es_recurso', 'es_portada')
    list_display_links = ('titulo',)
    fields = ('proveedor', 'titulo', 'fecha', 'descripcion', 'icono', 'identificador', 'duracion', 'es_recurso', 'es_portada', 'tags')
    form = MultimediaAdminForm

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class RecursoAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'descripcion', 'autor']
    list_display = ('fecha', 'titulo', 'tipo', 'es_portada')
    list_display_links = ('titulo',)
    fields = ('tipo', 'titulo', 'slug', 'fecha', 'icono', 'tags', 'descripcion', 'autor', 'articulo_blog', 'multimedia', 'isbn', 'enlace', 'archivo', 'contenido', 'es_portada')
    # readonly_fields = ('fecha', )
    prepopulated_fields = {'slug': ('titulo',)}
    form = RecursoAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(RecursoAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['articulo_blog'].queryset = Articulo.objects.all().order_by('-fecha')
        form.base_fields['multimedia'].queryset = Multimedia.objects.all().order_by('-fecha')
        return form

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class EtiquetaAdmin(DjangoMpttAdmin):
    tree_auto_open = 1
    list_display = ('name',)


class BlogAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'subtitulo', 'descripcion']
    list_display = ('titulo', 'subtitulo', 'url', 'autor', 'imagen_img')
    list_display_links = ('titulo',)
    fields = ('titulo', 'subtitulo', 'descripcion', 'url', 'codigo_urchin', 'gplus_profile', 'imagen', 'usuario', 'autor', 'subdominio', 'tiene_categorias', 'es_colectivo', 'multiidioma', 'tiene_destacados')


class AutorBlogAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email')
    fields = ('nombre', 'email', 'curriculum', 'foto')
    form = AutorBlogAdminForm

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class ArticuloAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'blog__titulo', 'subtitulo', 'autor__nombre', 'autor__apellidos']
    list_display = ('blog', 'seccion', 'titulo', 'subtitulo', 'autor', 'icono', 'fecha')
    list_display_links = ('titulo',)
    fields = ('blog', 'titulo', 'slug', 'subtitulo', 'autor', 'icono', 'contenido', 'fecha', 'inicio', 'seccion')
    readonly_fields = ('fecha', )
    prepopulated_fields = {'slug': ('titulo',)}
    form = ArticuloAdminForm

    def get_form(self, request, obj=None, **kwargs):
        excluidos = ()
        incluidos = ('blog', 'titulo', 'slug', 'subtitulo', 'autor', 'icono', 'contenido', 'fecha', 'inicio', 'seccion')
        if request.user.has_perm('can_admin_blogs'):
            incluidos += ('es_portada', 'es_destacado')
        if not request.user.has_perm('can_admin_blogs'):
            blog = get_object_or_404(Blog, usuario=request.user)
            if not blog.es_colectivo:
                excluidos += ('subtitulo', 'autor')
            if not blog.tiene_categorias:
                excluidos += ('seccion',)
        self.exclude = excluidos
        self.fields = tuple(f for f in incluidos if f not in excluidos)
        form = super(ArticuloAdmin, self).get_form(request, obj=None, **kwargs)
        # if not request.user.has_perm('can_admin_blogs'):
        #    form.base_fields['blog'].initial = blog
        #    form.base_fields['blog'].disabled = True
        #    raise(TypeError, '[blog: %s]' % blog)
        return form

    def changelist_view(self, request, extra_context=None):
        excluidos = ()
        lista_campos = ('blog', 'seccion', 'titulo', 'subtitulo', 'autor', 'icono', 'fecha')
        if request.user.has_perm('can_admin_blogs'):
            lista_campos += ('es_portada', 'es_destacado')
        if not request.user.has_perm('can_admin_blogs'):
            blog = get_object_or_404(Blog, usuario=request.user)
            if not blog.es_colectivo:
                excluidos += ('subtitulo', 'autor')
            if not blog.tiene_categorias:
                excluidos += ('seccion',)
        self.list_display = tuple(f for f in lista_campos if f not in excluidos)
        return super(ArticuloAdmin, self).changelist_view(request, extra_context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'blog':
            if request.user.has_perm('can_admin_blogs'):
                queryset = Blog.objects.all()
                return super(ArticuloAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
            else:
                queryset = Blog.objects.filter(usuario=request.user)
                return ModelChoiceField(queryset, initial=get_object_or_404(Blog, usuario=request.user))
        else:
            return super(ArticuloAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    # def get_readonly_fields(self, request, obj=None):
    #     fields = super(ArticuloAdmin, self).get_readonly_fields(request, obj)
    #     if not request.user.has_perm('can_admin_blogs'):
    #         fields += ('blog',)
    #     return fields

    def get_queryset(self, request):
        qs = super(ArticuloAdmin, self).get_queryset(request)
        if request.user.has_perm('opress.admin_blogs'):
            return qs
        return qs.filter(blog__usuario=request.user)

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]


class OtroBlogAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'autor', 'descripcion']
    list_display = ('titulo', 'tipo', 'url', 'autor', 'imagen_img')
    list_display_links = ('titulo',)
    fields = ('tipo', 'titulo', 'autor', 'descripcion', 'url', 'imagen', 'blog', 'rss', 'suscripcion_correo')


admin.site.unregister(Site)
admin.site.register(Sitio, SitioAdmin)
admin.site.register(PublicacionSitio, PublicacionSitioAdmin)

admin.site.register(Pagina, PaginaAdmin)
admin.site.register(Bloque, BloqueAdmin)
admin.site.register(Timeline, TimelineAdmin)
admin.site.register(FlickrUser, FlickrUserAdmin)
admin.site.register(Noticia, NoticiaAdmin)
admin.site.register(Agenda, AgendaAdmin)
admin.site.register(Documento, DocumentoAdmin)
admin.site.register(CategoriaDocumento, CategoriaDocumentoAdmin)
admin.site.register(Boletin, BoletinAdmin)
admin.site.register(Destacado, DestacadoAdmin)
admin.site.register(AparicionPrensa, AparicionPrensaAdmin)
admin.site.register(IPUser, IPUserAdmin)
admin.site.register(TipoMensaje)
admin.site.register(GoogleMap)
admin.site.register(PuntoGoogleMap)
admin.site.register(Multimedia, MultimediaAdmin)
admin.site.register(Recurso, RecursoAdmin)
admin.site.register(HierarchicalTag, EtiquetaAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(AutorBlog, AutorBlogAdmin)
admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(OtroBlog, OtroBlogAdmin)
admin.site.register(LocationTag)
