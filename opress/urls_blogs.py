from django.conf.urls import *
from .views import *

urlpatterns = patterns('',
    url(r'^$', blog_index, name='blog_index'),
    url(r'^comments/', include('fluent_comments.urls')),
    url(r'^(?P<year>[\d]+)/$', blog_archive, name='blog_archive'),
    url(r'^(?P<section>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/$', blog_article, name='blog_article'),
    url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', static_page, name='static_page'),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )