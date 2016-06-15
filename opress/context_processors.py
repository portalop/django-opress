from django.conf import settings # import the settings file
from django.contrib.sites.models import Site

def opress(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'IS_PRODUCTION': settings.PRODUCTION, 'COOKIE_WARNING': request.COOKIES.get('cookie_warning', None), 'SITE_URL': Site.objects.get_current().domain}
