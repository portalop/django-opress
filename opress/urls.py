from django.conf.urls import *
from .views import *

# Support for the tinymce-gallery-connection plugin
urlpatterns = patterns('',
    (r'^galleries', galleries),
    (r'^images/(\-?\d+)', images),
    (r'^image/(\d+)', image),
    (r'^image_src/(\d+)/(\w+)', image_src),
)