from django.conf.urls import include, url
from filebrowser.sites import site
from django.contrib import admin
from django.core.files.storage import DefaultStorage
from filebrowser.sites import FileBrowserSite
from views import MyIndexView
from opress.views import *

# Default FileBrowser site
site = FileBrowserSite(name='hispaniae', storage=DefaultStorage())
site.directory = "uploads/"

#admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'hispaniae.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^photologue/', include('photologue.urls', namespace='photologue')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^$', MyIndexView.as_view(), name='index'),
    url(r'^capitulo-provincial-2016/cronica/(?P<slug>[0-9A-Za-z-_.//]+)/$', document_detail, {'template': 'opress/capitulo2016/cronica.html', 'slug_pagina': 'capitulo-provincial-2016/cronica'}, name='cronica_detalle'),
    url(r'^capitulo-provincial-2016/album/(?P<id>[\d]+)/$', bloque_detail, {'template': 'opress/capitulo2016/album_flickr.html', 'slug_pagina': 'capitulo-provincial-2016/album'}, name='bloque_detail'),
    url(r'^', include('opress.urls', namespace='opress')),
    url(r'^admin/', include(admin.site.urls)),
]

handler404 = 'opress.views.error404'
