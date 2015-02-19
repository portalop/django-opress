from django.conf import settings # import the settings file

def opress(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'IS_PRODUCTION': settings.PRODUCTION, 'COOKIE_WARNING': request.COOKIES.get('cookie_warning')}
