from django.conf.urls import *
from .views import *
from .feeds import BlogFeed

app_name = "opress"
urlpatterns = [
    url(r'^$', blog_index, name='blog_index'),
    url(r'^rss/$', BlogFeed(), name='blog_rss'),
	url(r'^autor/(?P<slug>[0-9A-Za-z-_.//]+)/$', blog_autor, name='blog_autor'),
    url(r'^comments/', include('fluent_comments.urls')),
    url(r'^(?P<year>[\d]+)/$', blog_archive, name='blog_archive'),
    url(r'^(?P<section>[\-\d\w]+)/(?P<slug>[\-\d\w]+)/$', blog_article, name='blog_article'),
    #url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', static_page, name='static_page'),
    url(r'^', include('opress.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]