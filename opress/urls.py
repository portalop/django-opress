from django.conf.urls import *
from .views import *
from .feeds import NewsFeed, EventsFeed
from django.contrib import admin
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'noticias', NoticiaViewSet, 'noticia')
router.register(r'agendas', AgendaViewSet, 'agenda')
router.register(r'photos', PhotoViewSet)
router.register(r'sites', SiteViewSet)

CUSTOM_URLS = getattr(settings, 'OPRESS_CUSTOM_URLS', {
    'RESOURCES': r'^recursos/$',
    'RESOURCES_BY_TYPE': r'^recursos/tipo/(?P<mtype>(documento|video|audio|libro|resena))/$',
    'RESOURCES_BY_TAG': r'^recursos/tema/(?P<tag>[0-9A-Za-z-_.//]+)/$',
    'RESOURCES_BY_YEAR': r'^recursos/(?P<year>[\d]+)/$',
    'RESOURCE_MULTIMEDIA': r'^recursos/multimedia/(?P<mtype>(video|audio|album))/(?P<id>[0-9A-Za-z-_.//]+)/$',
    'RESOURCE': r'^recurso/(?P<slug>[0-9A-Za-z-_.//]+)/$',
})

app_name = "opress"
urlpatterns = [
    url(r'^admin/opress/galleries', galleries),
    url(r'^admin/opress/images/(\-?\d+)', images),
    url(r'^admin/opress/image/(\d+)', image),
    url(r'^admin/opress/image_src/(\d+)/(\w+)', image_src),
    url(r'^admin/opress/boletin/view/(\d+)', generar_boletin, name='generar_boletin'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^noticias/tema/(?P<tag>[\-\d\w]+)/$', NewsArchiveView.as_view(), name='news_tag'),
    url(r'^noticias/(?P<year>[\d]+)/$', NewsArchiveView.as_view(), name='news_archive'),
    url(r'^noticias/$', NewsView.as_view(), name='news'),
    url(r'^noticia/(?P<slug>[\-\d\w]+)/$', news_detail, name='news_detail'),
    url(r'^agenda/tema/(?P<tag>[\-\d\w]+)/$', events_archive, name='events_tag'),
    url(r'^agenda/(?P<year>[\d]+)/(?P<month>[\d]+)/$', events_archive, name='events_archive'),
    url(r'^agenda/$', events, name='events'),
    url(r'^evento/(?P<slug>[\-\d\w]+)/$', event_detail, name='event_detail'),
    url(r'^documentos/(?P<slug>[0-9A-Za-z-_.//]+)/$', documents_archive, name='documents_archive'),
    url(r'^documentos/$', documents, name='documents'),
    url(r'^documento/(?P<slug>[0-9A-Za-z-_.//]+)/$', document_detail, name='document_detail'),
    url(r'^multimedia/$', MultimediaView.as_view(), name='multimedia'),
    url(r'^multimedia/tipo/(?P<mtype>(video|audio|album))/$', MultimediaArchivoView.as_view(), name='multimedia_tipo'),
    url(r'^multimedia/tema/(?P<tag>[\-\d\w]+)/$', MultimediaArchivoView.as_view(), name='multimedia_tag'),
    url(r'^multimedia/(?P<year>[\d]+)/$', MultimediaArchivoView.as_view(), name='multimedia_archive'),
    url(r'^(?P<mtype>(video|audio|album))/(?P<id>[0-9A-Za-z-_.//]+)/$', MultimediaDetailView.as_view(), name='multimedia_detail'),
    url(CUSTOM_URLS['RESOURCES_BY_TYPE'], RecursosArchivoView.as_view(), name='recursos_tipo'),
    url(CUSTOM_URLS['RESOURCES_BY_TAG'], RecursosArchivoView.as_view(), name='recursos_etiqueta'),
    url(CUSTOM_URLS['RESOURCES_BY_YEAR'], RecursosArchivoView.as_view(), name='recursos_archivo'),
    url(CUSTOM_URLS['RESOURCES'], RecursosView.as_view(), name='recursos'),
    url(CUSTOM_URLS['RESOURCE_MULTIMEDIA'], RecursoView.as_view(), name='recurso_multimedia'),
    url(CUSTOM_URLS['RESOURCE'], RecursoView.as_view(), name='recurso'),
    url(r'^buscar-mas/(?P<filtro>\w+)/$', search_more, name='search_more'),
    url(r'^buscar/(?P<filtro>\w+)/$', search, name='search'),
    url(r'^buscar/$', search, name='search'),
    url(r'^contactar/$', contact, name='contact'),
    url(r'^rss/noticias/$', NewsFeed(), name='news_rss'),
    url(r'^rss/agenda/$', EventsFeed(), name='events_rss'),
    url(r'^opress-api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', static_page, name='static_page')
]
