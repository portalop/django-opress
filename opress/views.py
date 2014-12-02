from datetime import datetime
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from photologue.models import Gallery, Photo, PhotoSize
import json
from .models import Pagina, Noticia, Agenda, Bloque, Destacado
from django.conf import settings

def galleries(request):
    format = request.GET.get('format', 'json')
    galleries = map(lambda g: {'id': g.pk, 'title': g.title, 'desc': g.description}, Gallery.objects.all())
    data = json.dumps(galleries)
    if request.GET.has_key('jsoncallback'):
        data = request.GET['jsoncallback'] + '(' + data + ')'
        return HttpResponse(data, content_type="application/javascript")
    return HttpResponse(data, content_type="application/json")

def images(request, gallery_id):
    gallery_id = int(gallery_id)
    queryset = Gallery.objects.get(id__exact=gallery_id).photos.all().reverse()[:15] if (gallery_id > -1) else Photo.objects.filter(galleries=None)[:15]
    images = map(lambda i: {'id': i.pk, 'title': i.title, 'desc': i.caption, 'thumb': i.get_admin_thumbnail_url()}, queryset)
    data = json.dumps(images)
    if request.GET.has_key('jsoncallback'):
        data = request.GET['jsoncallback'] + '(' + data + ')'
        return HttpResponse(data, content_type="application/javascript")
    return HttpResponse(data, content_type="application/json")

def image(request, photo_id):
    photo = Photo.objects.get(id__exact=photo_id)
    data = json.dumps({'id': photo.pk, 'title': photo.title, 'desc': photo.caption, 'thumb': photo.get_admin_thumbnail_url()})
    if request.GET.has_key('jsoncallback'):
        data = request.GET['jsoncallback'] + '(' + data + ')'
        return HttpResponse(data, content_type="application/javascript")
    return HttpResponse(data, content_type="application/json")

def image_src(request, photo_id, size_id):
    photo = Photo.objects.get(id__exact=photo_id)
    size = PhotoSize.objects.get(name=size_id)
    data = '{\'size_id\':\'' + size_id + '\', \'src\':\'' + photo._get_SIZE_url(size_id) + '\'}'
    if request.GET.has_key('jsoncallback'):
        data = request.GET['jsoncallback'] + '(' + data + ')'
        return HttpResponse(data, content_type="application/javascript")
    return HttpResponse(data, content_type="text")

def index(request):
    news_list = Noticia.objects.filter(fecha__lt=datetime.now()).order_by('-fecha')[:4]
    agenda_list = Agenda.objects.filter(fecha_fin__gte=datetime.now().date()).order_by('fecha_inicio')[:4]
    slider_list = Destacado.objects.filter(visible=True)
    return render(request, 'opress/index.html', {'arbol_paginas': Pagina.objects.filter(in_menu=True), 'seccion': None, 'news_list': news_list, 'agenda_list': agenda_list, 'slider_list': slider_list})

def static_page(request, slug):
    if slug == 'noticia':
        raise Http404
    for pagina in Pagina.objects.filter(slug=slug.split('/')[-1]):
        if pagina.get_url() == slug:
            pagina.contenido = pagina.contenido.replace('"/media/', '"' + settings.MEDIA_URL).replace("'/media/", "'" + settings.MEDIA_URL)
            bloque_list = Bloque.objects.filter(se_hereda=True, paginas_cabecera__in=(pagina.get_ancestors())) | pagina.bloques_cabecera.all()
            if pagina.is_child_node():
                arbol_seccion = pagina.get_ancestors(include_self=True) | pagina.get_children() | pagina.get_root().get_children() | pagina.get_siblings()
                seccion = pagina.get_root()
                arbol_seccion = arbol_seccion.exclude(pk=seccion.pk)
            else:
                arbol_seccion = pagina.get_children()
                seccion = pagina
            return render(request, 'opress/static_page.html', {'pagina': pagina, 'bloque_list': bloque_list, 'arbol_paginas': Pagina.objects.filter(in_menu=True), 'arbol_seccion': arbol_seccion, 'seccion': seccion})
    raise Http404

def news_detail(request, slug):
    pagina_noticias = None
    for pagina in Pagina.objects.filter(slug='noticia'):
        if pagina.get_url() == 'noticia':
            pagina_noticias = pagina
    noticia = get_object_or_404(Noticia, slug=slug)
    news_list = Noticia.objects.filter(~Q(slug=slug), fecha__lte=noticia.fecha, fecha__lt=datetime.now()).order_by('-fecha')[:4]

    id_list = list(Noticia.objects.filter(fecha__lt=datetime.now()).order_by('-fecha').values_list('id', flat=True))
    try:
        noticia_siguiente = None
        noticia_anterior = None
        if id_list.index(noticia.id) < len(id_list) - 1:
            noticia_siguiente = Noticia.objects.get(id=id_list[id_list.index(noticia.id) + 1])
        if id_list.index(noticia.id) > 0:
            noticia_anterior = Noticia.objects.get(id=id_list[id_list.index(noticia.id) - 1])
    except IndexError:
        pass

    noticia.contenido = noticia.contenido.replace('"/media/', '"' + settings.MEDIA_URL).replace("'/media/", "'" + settings.MEDIA_URL)
    return render(request, 'opress/news_detail.html', {'noticia': noticia, 'noticia_siguiente': noticia_siguiente, 'noticia_anterior': noticia_anterior, 'pagina': pagina_noticias, 'arbol_paginas': Pagina.objects.filter(in_menu=True), 'seccion': pagina_noticias.get_root(), 'historico': Noticia.objects.filter(fecha__lt=datetime.now()).dates('fecha', 'year', order='DESC'), 'news_list': news_list})

def news_archive(request, year):
    pagina_noticias = None
    for pagina in Pagina.objects.filter(slug='noticias'):
        if pagina.get_url() == 'noticias':
            pagina_noticias = pagina
    news_list = Noticia.objects.filter(fecha__lt=datetime.now()).order_by('-fecha')
    if year:
        news_list = news_list.filter(fecha__year=year)
    paginator = Paginator(news_list, 20)
    page = request.GET.get('page')
    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        news_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        news_list = paginator.page(paginator.num_pages)
    return render(request, 'opress/news.html', {'pagina': pagina_noticias, 'arbol_paginas': Pagina.objects.filter(in_menu=True), 'seccion': pagina_noticias.get_root(), 'news_list': news_list, 'year': year, 'historico': Noticia.objects.filter(fecha__lt=datetime.now()).dates('fecha', 'year', order='DESC')})

def news(request):
    return news_archive(request, None)