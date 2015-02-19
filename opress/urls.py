from django.conf.urls import *
from .views import *
from django.contrib import admin

urlpatterns = patterns('',
    (r'^admin/opress/galleries', galleries),
    (r'^admin/opress/images/(\-?\d+)', images),
    (r'^admin/opress/image/(\d+)', image),
    (r'^admin/opress/image_src/(\d+)/(\w+)', image_src),
    url(r'^admin/opress/boletin/view/(\d+)', generar_boletin, name='generar_boletin'),
    (r'^admin/', include(admin.site.urls)),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^noticias/(?P<year>[\d]+)/$', news_archive, name='news_archive'),
    url(r'^noticias/$', news, name='news'),
    url(r'^noticia/(?P<slug>[\-\d\w]+)/$', news_detail, name='news_detail'),
    url(r'^agenda/(?P<year>[\d]+)/(?P<month>[\d]+)/$', events_archive, name='events_archive'),
    url(r'^agenda/$', events, name='events'),
    url(r'^evento/(?P<slug>[\-\d\w]+)/$', event_detail, name='event_detail'),
    url(r'^documentos/(?P<slug>[0-9A-Za-z-_.//]+)/$', documents_archive, name='documents_archive'),
    url(r'^documentos/$', documents, name='documents'),
    url(r'^documento/(?P<slug>[0-9A-Za-z-_.//]+)/$', document_detail, name='document_detail'),
    url(r'^buscar-mas/(?P<filtro>\w+)/$', search_more, name='search_more'),
    url(r'^buscar/(?P<filtro>\w+)/$', search, name='search'),
    url(r'^buscar/$', search, name='search'),
    url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', static_page, name='static_page')
)