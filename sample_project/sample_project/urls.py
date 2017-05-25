from django.conf.urls import include, url
from filebrowser.sites import site
from django.contrib import admin
from django.core.files.storage import DefaultStorage
from filebrowser.sites import FileBrowserSite
from views import MyIndexView
from opress.views import *

# Default FileBrowser site
site = FileBrowserSite(name='[:SAMPLE_PROJECT:]', storage=DefaultStorage())
site.directory = "uploads/"

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^photologue/', include('photologue.urls', namespace='photologue')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^$', MyIndexView.as_view(), name='index'),
    url(r'^', include('opress.urls', namespace='opress')),
    url(r'^admin/', include(admin.site.urls)),
]

handler404 = 'opress.views.error404'
