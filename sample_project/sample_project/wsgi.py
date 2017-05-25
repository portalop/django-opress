"""
WSGI config for [:SAMPLE_PROJECT:] project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
from [:SAMPLE_PROJECT:] import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "[:SAMPLE_PROJECT:].settings")
import django
django.setup()
try:
    import uwsgi
    from uwsgidecorators import timer
    from django.utils import autoreload
except:
    pass

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

try:
    @timer(3)
    def change_code_gracefull_reload(sig):
        if autoreload.code_changed():
            uwsgi.reload()
except:
    pass
