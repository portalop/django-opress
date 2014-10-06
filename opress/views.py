from django.http import HttpResponse
from photologue.models import Gallery, Photo, PhotoSize
from django.utils import simplejson

def galleries(request):
    format = request.GET.get('format', 'json')
    galleries = map(lambda g: {'id': g.pk, 'title': g.title, 'desc': g.description}, Gallery.objects.all())
    data = simplejson.dumps(galleries)
    if request.GET.has_key('jsoncallback'):
        data = request.GET['jsoncallback'] + '(' + data + ')'
        return HttpResponse(data, mimetype="application/javascript")
    return HttpResponse(data, mimetype="application/json")

def images(request, gallery_id):
    gallery_id = int(gallery_id)
    queryset = Gallery.objects.get(id__exact=gallery_id).photos.all().reverse()[:15] if (gallery_id > -1) else Photo.objects.filter(galleries=None)[:15]
    images = map(lambda i: {'id': i.pk, 'title': i.title, 'desc': i.caption, 'thumb': i.get_admin_thumbnail_url()}, queryset)
    data = simplejson.dumps(images)
    if request.GET.has_key('jsoncallback'):
        data = request.GET['jsoncallback'] + '(' + data + ')'
        return HttpResponse(data, mimetype="application/javascript")
    return HttpResponse(data, mimetype="application/json")

def image(request, photo_id):
    photo = Photo.objects.get(id__exact=photo_id)
    data = simplejson.dumps({'id': photo.pk, 'title': photo.title, 'desc': photo.caption, 'thumb': photo.get_admin_thumbnail_url()})
    if request.GET.has_key('jsoncallback'):
        data = request.GET['jsoncallback'] + '(' + data + ')'
        return HttpResponse(data, mimetype="application/javascript")
    return HttpResponse(data, mimetype="application/json")

def image_src(request, photo_id, size_id):
    photo = Photo.objects.get(id__exact=photo_id)
    size = PhotoSize.objects.get(name=size_id)
    data = '{\'size_id\':\'' + size_id + '\', \'src\':\'' + photo._get_SIZE_url(size_id) + '\'}'
    if request.GET.has_key('jsoncallback'):
        data = request.GET['jsoncallback'] + '(' + data + ')'
        return HttpResponse(data, mimetype="application/javascript")
    return HttpResponse(data, mimetype="text")
