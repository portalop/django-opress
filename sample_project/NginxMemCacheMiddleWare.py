from django.core.cache import cache
import re
from django.conf import settings

class NginxMemCacheMiddleWare:
    def process_response(self, request, response):
        cacheIt = True
        theUrl = request.get_full_path()

        if hasattr(request, 'user'):
            if request.user.is_authenticated() and not request.COOKIES.get('cache'):
                response.set_cookie("cache", 'no')
            elif not request.user.is_authenticated() and request.COOKIES.get('cache'):
                response.delete_cookie("cache")

            if request.user.is_authenticated() or request.COOKIES.get('cookie_warning', None) != "ok" or response.status_code != 200:
                cacheIt = False

        # if it's a GET then store it in the cache:
        if request.method != 'GET':
            cacheIt = False

        # loop on our CACHE_INGORE_REGEXPS and ignore
        # certain urls.
        for exp in settings.CACHE_IGNORE_REGEXPS:
            if re.match(exp,theUrl):
                cacheIt = False

        if cacheIt:
            # key = '%s-%s' % (settings.CACHE_KEY_PREFIX,theUrl)
            cache.set(theUrl, response.content)     

        return response
