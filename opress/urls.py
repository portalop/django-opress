from django.conf.urls import *
from .views import *
from django.contrib import admin
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'noticias', NoticiaViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'sites', SiteViewSet)

urlpatterns = [
    url(r'^admin/opress/galleries', galleries),
    url(r'^admin/opress/images/(\-?\d+)', images),
    url(r'^admin/opress/image/(\d+)', image),
    url(r'^admin/opress/image_src/(\d+)/(\w+)', image_src),
    url(r'^admin/opress/boletin/view/(\d+)', generar_boletin, name='generar_boletin'),
    url(r'^admin/', include(admin.site.urls)),
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
    url(r'^contactar/$', contact, name='contact'),
    url(r'^opress-api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', static_page, name='static_page')
]