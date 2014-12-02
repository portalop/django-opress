from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import Pagina, Bloque, Noticia, Agenda, Timeline, TimelineItem, FlickrUser, Documento, CategoriaDocumento, Destacado, BLOCK_TYPE_CHOICES
from django.conf import settings
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django_mptt_admin.admin import DjangoMpttAdmin
from tinymce.widgets import TinyMCE
from photologue.models import PhotoSize, Photo, Gallery
from photologue.fields import PhotoFormField
import json

def dimensiones(numero):
    if numero==0:
        return('proporcional')
    else:
        return('%s px' % numero)

def get_add_link(model):
    return(reverse(
                'admin:%s_%s_add' % (model._meta.app_label, model._meta.object_name.lower()), current_app=admin.site.name
            ))

OPRESS_TINYMCE_DEFAULT_CONFIG = {
    'gallerycon_settings': settings.TINYMCE_DEFAULT_CONFIG['gallerycon_settings']
}

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
    def __init__(self, *args, **kwargs):
        request = self.request
        super(PaginaAdminForm, self).__init__(*args,**kwargs)
        init_gallerycon_settings()
        if 'parent_id' in request.GET:
            self.fields['parent'].initial = Pagina.objects.get(pk=request.GET.get('parent_id'))

class BloqueAdminForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=BLOCK_TYPE_CHOICES, widget=forms.Select(attrs={"class":"select_block", "onChange":"hide_fields(this)"}))
    contenido = forms.CharField(required=False, widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 300})))
    def __init__(self, *args, **kwargs):
        super(BloqueAdminForm, self).__init__(*args,**kwargs)
        init_gallerycon_settings()

    class Media:
        js = [
            settings.STATIC_URL + 'opress/js/opress.js',
        ]

class NoticiaAdminForm(forms.ModelForm):
    contenido = forms.CharField(widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))
    def __init__(self, *args, **kwargs):
        super(NoticiaAdminForm, self).__init__(*args,**kwargs)
        init_gallerycon_settings()

class AgendaAdminForm(forms.ModelForm):
    contenido = forms.CharField(widget=TinyMCE(mce_attrs=customize_tinyMCE({'width': 980, 'height': 600})))
    def __init__(self, *args, **kwargs):
        super(AgendaAdminForm, self).__init__(*args,**kwargs)
        init_gallerycon_settings()

class CategoriaDocumentoAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = self.request
        super(CategoriaDocumentoAdminForm, self).__init__(*args,**kwargs)
        if 'parent_id' in request.GET:
            self.fields['parent'].initial = CategoriaDocumento.objects.get(pk=request.GET.get('parent_id'))

class StackedInlineWithoutWidgetWrapper(admin.StackedInline):
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)
    def formfield_for_dbfield(self, db_field, **kwargs):
        old_formfield = admin.StackedInline.formfield_for_dbfield(self, db_field,
            **kwargs)
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
            'fields' : ()
        }),
        ('Contenido', {
            'fields': ('contenido',),
        }),
        ('Pie', {
            'classes': ('placeholder bloques_pie-group',),
            'fields' : ()
        }),
        ('Configuración avanzada', {
            'fields': (('in_menu', 'menu'), 'imagen_cabecera', 'template_url', 'es_seccion'),
        })
    )
    form = PaginaAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form_with_request = super(PaginaAdmin, self).get_form(request, obj=None, **kwargs)
        form_with_request.request = request
        return form_with_request

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]

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
    fields = ('titulo', 'slug', 'fecha', 'entradilla', 'icono', 'imagen', 'tags', 'contenido')
    prepopulated_fields = {'slug': ('titulo',)}
    inlines = [BloqueNoticiaInline]
    form = NoticiaAdminForm

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]

class AgendaAdmin(admin.ModelAdmin):
    search_fields = ['titulo', 'entradilla', 'fecha_inicio']
    list_display = ('icono_img', 'fecha_inicio', 'fecha_fin', 'titulo', 'entradilla')
    list_display_links = ('titulo',)
    fields = ('titulo', 'slug', 'fecha_inicio', 'fecha_fin', 'entradilla', 'icono', 'tags', 'contenido', ('se_anuncia', 'inicio_anuncio', 'fin_anuncio',), 'es_periodico', ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'))
    prepopulated_fields = {'slug': ('titulo',), 'fin_anuncio': ('fecha_inicio',)}
    form = AgendaAdminForm

    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]

class DocumentoInline(admin.StackedInline):
    inline_classes = ('grp-collapse grp-open',)
    model = Documento
    extra = 0

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

admin.site.register(Pagina, PaginaAdmin)
admin.site.register(Bloque, BloqueAdmin)
admin.site.register(Timeline, TimelineAdmin)
admin.site.register(FlickrUser, FlickrUserAdmin)
admin.site.register(Noticia, NoticiaAdmin)
admin.site.register(Agenda, AgendaAdmin)
admin.site.register(CategoriaDocumento, CategoriaDocumentoAdmin)
admin.site.register(Destacado)
