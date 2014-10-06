from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import Pagina
from django.conf import settings
from django_mptt_admin.admin import DjangoMpttAdmin
from tinymce.widgets import TinyMCE
from photologue.models import PhotoSize, Photo, Gallery

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
    #OPRESS_TINYMCE_DEFAULT_CONFIG['gallerycon_settings']['default_size'] = PhotoSize.objects.get(name='normal').id

class PaginaAdminForm(forms.ModelForm):
    contenido = forms.CharField(widget=TinyMCE(mce_attrs=OPRESS_TINYMCE_DEFAULT_CONFIG))
    def __init__(self, *args, **kwargs):
        super(PaginaAdminForm, self).__init__(*args,**kwargs)
        init_gallerycon_settings()
        OPRESS_TINYMCE_DEFAULT_CONFIG.update({'width': 980, 'height': 600})

class PaginaAdmin(DjangoMpttAdmin):
    search_fields = ['titulo']
    tree_auto_open = 0
    list_display = ('titulo',)
    prepopulated_fields = {'slug': ('titulo',)}
    fieldsets = (
        ('Datos generales', {
            'fields': ('titulo', 'slug', 'icono', 'parent', 'descripcion', 'contenido'),
        }),
        ('Configuración avanzada', {
            'fields': (('in_menu', 'menu'), 'imagen_cabecera', 'template_url', 'es_seccion'),
        })
    )
    form = PaginaAdminForm
    class Media:
        js = [
            settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        ]

admin.site.register(Pagina, PaginaAdmin)
