from django.conf.urls import *
from .views import *
from django.contrib import admin

# Support for the tinymce-gallery-connection plugin
urlpatterns = patterns('',
    (r'^admin/opress/galleries', galleries),
    (r'^admin/opress/images/(\-?\d+)', images),
    (r'^admin/opress/image/(\d+)', image),
    (r'^admin/opress/image_src/(\d+)/(\w+)', image_src),
    (r'^admin/', include(admin.site.urls)),
    (r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', static_page)
)