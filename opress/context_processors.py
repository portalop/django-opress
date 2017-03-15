from django.conf import settings # import the settings file
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse, NoReverseMatch

def opress(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    try:
    	reverse('opress:static_page', kwargs={'slug': settings.OPRESS_COOKIES_URL})
    	COOKIE_WARNING = request.COOKIES.get('cookie_warning', None)
    except NoReverseMatch:
    	COOKIE_WARNING = 'ok'

    return {'IS_PRODUCTION': settings.PRODUCTION, 'COOKIE_WARNING': COOKIE_WARNING, 'SITE_URL': Site.objects.get_current().domain}
