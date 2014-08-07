from django.contrib import admin
from pages.models import Pagina
from photologue.models import Photo
from django_mptt_admin.admin import DjangoMpttAdmin

class PaginaAdmin(DjangoMpttAdmin):
    search_fields = ['titulo']
    tree_auto_open = 0
    list_display = ('titulo',)
    readonly_fields = ('page_icon',)
    fields = ('titulo', 'icono', 'page_icon', 'parent')

admin.site.register(Pagina, PaginaAdmin)
