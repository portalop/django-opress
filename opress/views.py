# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.db.models import Q
from django.core.mail import EmailMessage
from photologue.models import Gallery, Photo, PhotoSize
import json
import itertools
from .models import Pagina, Noticia, Agenda, Bloque, Destacado, Documento, CategoriaDocumento, Boletin, TipoMensaje, Blog, Articulo
from .search import get_query
from .forms import MensajeForm
from django.conf import settings
from ipware.ip import get_ip
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from rest_framework import viewsets, mixins
from .serializers import UserSerializer, GroupSerializer, NoticiaSerializer, PhotoSerializer, SiteSerializer

def set_warning_cookie(the_func):
    """
    Set the cookie to disable the cookie warnings
    """
    def _decorated(*args, **kwargs):
        response = the_func(*args, **kwargs)
        response.set_cookie('cookie_warning', 'ok') 
        return response
    _decorated.__doc__=the_func.__doc__
    _decorated.__name__=the_func.__name__
    return _decorated

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

class IndexView(View):
    def get_additional_content(self):
        pass

    @set_warning_cookie
    def get(self, request):
        news_list = Noticia.objects.select_related('icono').filter(fecha__lte=datetime.now()).order_by('-fecha')[:6]
        agenda_list = Agenda.objects.select_related('icono').filter(fecha_fin__gte=datetime.now().date()).order_by('fecha_inicio')[:3]
        slider_list = Destacado.objects.select_related('imagen').filter(Q(fecha__lte=datetime.now()) | Q(fecha__isnull=True), visible=True).order_by('-fecha', '-id')
        return render(request, 'opress/index.html', {'arbol_paginas': Pagina.objects.get_menu(), 'seccion': None, 'news_list': news_list, 'agenda_list': agenda_list, 'slider_list': slider_list, 'additional_content': self.get_additional_content(), 'pagina': None})

@set_warning_cookie
def static_page(request, slug):
    if slug == 'noticia':
        raise Http404
    for pagina in Pagina.objects.filter(slug=slug.split('/')[-1]):
        if pagina.get_url() == slug:
            pagina.ancestros = pagina.get_ancestors()
            pagina.contenido = pagina.contenido.replace('"/media/', '"' + settings.MEDIA_URL).replace("'/media/", "'" + settings.MEDIA_URL)
            bloque_list = Bloque.objects.filter(se_hereda=True, paginas_cabecera__in=(pagina.get_ancestors())) | pagina.bloques_cabecera.all()
            slider_list = pagina.destacado_set.filter(Q(fecha__lte=datetime.now()) | Q(fecha__isnull=True)).order_by('-fecha', '-id')
            document_list = list(itertools.chain(*[p.categoriadocumento_set.all() for p in pagina.get_descendants(include_self=True)]))
            if pagina.is_child_node():
                seccion = pagina.get_root()
                arbol_seccion = pagina.get_ancestors(include_self=True) | pagina.get_children() | seccion.get_children() | pagina.get_siblings()
                arbol_seccion = arbol_seccion.exclude(pk=seccion.pk)
            else:
                arbol_seccion = pagina.get_children()
                seccion = pagina
            return render(request, pagina.get_template() or 'opress/static_page.html', {'pagina': pagina, 'bloque_list': bloque_list, 'slider_list': slider_list, 'document_list': document_list, 'arbol_paginas': Pagina.objects.get_menu(), 'arbol_seccion': arbol_seccion.filter(in_menu=True), 'seccion': seccion, 'menu_microsite': seccion.get_descendants().filter(in_menu=True)})
    raise Http404

@set_warning_cookie
def news_detail(request, slug):
    pagina_noticias = None
    for pagina in Pagina.objects.filter(slug='noticia'):
        if pagina.get_url() == 'noticia':
            pagina.ancestros = pagina.get_ancestors()
            pagina_noticias = pagina
    noticia = get_object_or_404(Noticia, slug=slug, fecha__lte=datetime.now())
    news_list = Noticia.objects.filter(~Q(slug=slug), fecha__lte=min([noticia.fecha, datetime.now().date()])).order_by('-fecha')[:4]

    id_list = list(Noticia.objects.filter(fecha__lte=datetime.now()).order_by('-fecha').values_list('id', flat=True))
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
    return render(request, 'opress/news_detail.html', {'noticia': noticia, 'noticia_siguiente': noticia_siguiente, 'noticia_anterior': noticia_anterior, 'pagina': pagina_noticias, 'arbol_paginas': Pagina.objects.get_menu(), 'seccion': pagina_noticias.get_root(), 'menu_microsite': pagina_noticias.get_root().get_descendants().filter(in_menu=True), 'historico': Noticia.objects.filter(fecha__lt=datetime.now()).dates('fecha', 'year', order='DESC'), 'news_list': news_list})

@set_warning_cookie
def news_archive(request, year):
    pagina_noticias = None
    for pagina in Pagina.objects.filter(slug='noticias'):
        if pagina.get_url() == 'noticias':
            pagina.ancestros = pagina.get_ancestors()
            pagina_noticias = pagina
    news_list = Noticia.objects.filter(fecha__lte=datetime.now()).order_by('-fecha')
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
    return render(request, 'opress/news.html', {'pagina': pagina_noticias, 'arbol_paginas': Pagina.objects.get_menu(), 'seccion': pagina_noticias.get_root(), 'menu_microsite': pagina_noticias.get_root().get_descendants().filter(in_menu=True), 'news_list': news_list, 'year': year, 'historico': Noticia.objects.filter(fecha__lt=datetime.now()).dates('fecha', 'year', order='DESC')})

@set_warning_cookie
def news(request):
    return news_archive(request, None)

@set_warning_cookie
def events_archive(request, year, month):
    pagina_agenda = None
    for pagina in Pagina.objects.filter(slug='agenda'):
        if pagina.get_url() == 'agenda':
            pagina.ancestros = pagina.get_ancestors()
            pagina_agenda = pagina
    events_list = Agenda.objects.filter(fecha_fin__gte=datetime.now()).order_by('fecha_inicio')
    if year and month:
        events_list = events_list.filter(fecha_inicio__year=year, fecha_inicio__month=month)
    paginator = Paginator(events_list, 20)
    page = request.GET.get('page')
    try:
        events_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        events_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        events_list = paginator.page(paginator.num_pages)
    return render(request, 'opress/events.html', {'pagina': pagina_agenda, 'arbol_paginas': Pagina.objects.get_menu(), 'seccion': pagina_agenda.get_root(), 'menu_microsite': pagina_agenda.get_root().get_descendants().filter(in_menu=True), 'events_list': events_list, 'meses': Agenda.objects.filter(fecha_inicio__gte=datetime.today()).dates('fecha_inicio', 'month', order='ASC'), 'anyo_actual': year, 'mes_actual': month})

@set_warning_cookie
def events(request):
    return events_archive(request, None, None)

@set_warning_cookie
def event_detail(request, slug):
    pagina_agenda = None
    for pagina in Pagina.objects.filter(slug='evento'):
        if pagina.get_url() == 'evento':
            pagina.ancestros = pagina.get_ancestors()
            pagina_agenda = pagina
    evento = get_object_or_404(Agenda, slug=slug)
    events_list = Agenda.objects.filter(~Q(slug=slug), fecha_inicio__gte=max(evento.fecha_inicio, datetime.now().date())).order_by('fecha_inicio')[:4]

    evento.contenido = evento.contenido.replace('"/media/', '"' + settings.MEDIA_URL).replace("'/media/", "'" + settings.MEDIA_URL)
    return render(request, 'opress/event_detail.html', {'evento': evento, 'pagina': pagina_agenda, 'arbol_paginas': Pagina.objects.get_menu(), 'seccion': pagina_agenda.get_root(), 'menu_microsite': pagina_agenda.get_root().get_descendants().filter(in_menu=True), 'events_list': events_list, 'meses': Agenda.objects.filter(fecha_inicio__gte=datetime.today()).dates('fecha_inicio', 'month', order='ASC')})

@set_warning_cookie
def documents_archive(request, slug):
    pagina_documentos = None
    for pagina in Pagina.objects.filter(slug='documentos'):
        if pagina.get_url() == 'documentos':
            pagina.ancestros = pagina.get_ancestors()
            pagina_documentos = pagina
    documents_list = Documento.objects.all().order_by("-fecha")
    categoria = categorias = None
    if slug:
        for cat in CategoriaDocumento.objects.filter(slug=slug.split('/')[-1]):
            if cat.get_url() == slug:
                categoria = cat
        documents_list = documents_list.filter(categoria_id__in=categoria.get_descendants(include_self=True))
        categorias = categoria.get_ancestors(include_self=True) | categoria.get_children() | categoria.get_root().get_children() | categoria.get_siblings()
    else:
        categorias = CategoriaDocumento.objects.filter(level=0)
    paginator = Paginator(documents_list, 20)
    page = request.GET.get('page')
    try:
        documents_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        documents_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        documents_list = paginator.page(paginator.num_pages)
    return render(request, 'opress/documents.html', {'pagina': pagina_documentos, 'arbol_paginas': Pagina.objects.get_menu(), 'seccion': pagina_documentos.get_root(), 'menu_microsite': pagina_documentos.get_root().get_descendants().filter(in_menu=True), 'documents_list': documents_list, 'categorias': categorias, 'categoria_actual': categoria})

@set_warning_cookie
def documents(request):
    return documents_archive(request, None)

@set_warning_cookie
def document_detail(request, slug, template='opress/document_detail.html', slug_pagina='documento'):
    pagina_documento = None
    for pagina in Pagina.objects.filter(slug=slug_pagina.split('/')[-1]):
        if pagina.get_url() == slug_pagina:
            pagina.ancestros = pagina.get_ancestors()
            pagina_documento = pagina
    slug_documento, slug_categoria = slug.split('/')[-1], slug.split('/')[-2]
    for doc in Documento.objects.filter(slug=slug_documento):
        if doc.get_url() == slug:
            documento = doc
            categoria = documento.categoria
    documents_list = Documento.objects.filter(~Q(slug=slug_documento), categoria=documento.categoria)[:4]
    categorias = categoria.get_ancestors(include_self=True) | categoria.get_children() | categoria.get_root().get_children() | categoria.get_siblings()

    documento.descripcion = documento.descripcion.replace('"/media/', '"' + settings.MEDIA_URL).replace("'/media/", "'" + settings.MEDIA_URL)
    return render(request, template, {'documento': documento, 'pagina': pagina_documento, 'arbol_paginas': Pagina.objects.get_menu(), 'seccion': pagina_documento.get_root(), 'menu_microsite': pagina_documento.get_root().get_descendants().filter(in_menu=True), 'documents_list': documents_list, 'categorias': categorias})

@set_warning_cookie
def bloque_detail(request, id, template='opress/bloque_detail.html', slug_pagina='bloque'):
    pagina_bloque = None
    for pagina in Pagina.objects.filter(slug=slug_pagina.split('/')[-1]):
        if pagina.get_url() == slug_pagina:
            pagina.ancestros = pagina.get_ancestors()
            pagina_bloque = pagina
    bloque = get_object_or_404(Bloque, id=id, tipo='flickr')
    return render(request, template, {'bloque': bloque, 'pagina': pagina_bloque, 'arbol_paginas': Pagina.objects.get_menu(), 'seccion': pagina_bloque.get_root(), 'menu_microsite': pagina_bloque.get_root().get_descendants().filter(in_menu=True)})

@staff_member_required
def generar_boletin(request, boletin_id):
    boletin = get_object_or_404(Boletin, id=boletin_id)
    news_list = list(Noticia.objects.filter(fecha__gte=boletin.fecha_inicio, fecha__lte=boletin.fecha_fin).order_by('fecha'))
    boletin.cabecera = boletin.cabecera.replace(' class="left"', 'align="left" hspace="10"').replace(' class="right"', 'align="right" hspace="10"')
    boletin.pie = boletin.pie.replace(' class="left"', 'align="left" hspace="10"').replace(' class="right"', 'align="right" hspace="10"')
    for noticia in news_list:
        noticia.contenido = noticia.contenido.replace(' class="left"', 'align="left" hspace="10"').replace(' class="right"', 'align="right" hspace="10"')
    return render(request, 'opress/newsletter.html', {'news_list': news_list, 'newsletter': boletin})

@set_warning_cookie
def search(request, filtro=""):
    pagina_buscar = None
    for pagina in Pagina.objects.filter(slug='buscar'):
        if pagina.get_url() == 'buscar':
            pagina.ancestros = pagina.get_ancestors()
            pagina_buscar = pagina
    query_string = ''
    found_pages = None
    found_news = None
    found_events = None
    found_documents = None
    last_entry = {'pages': False, 'news': False, 'events': False, 'documents': False}
    if filtro == '':
        num_results = 5
    else:
        num_results = 10
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        if filtro == 'pagina' or filtro == '':
            entry_query = get_query(query_string, ['titulo', 'descripcion', 'menu', 'contenido'])
            found_pages = Pagina.objects.filter(entry_query)[:num_results]
            last_entry['pages'] = not Pagina.objects.filter(entry_query)[num_results + 1:].exists()
        if filtro == 'noticia' or filtro == '':
            entry_query = get_query(query_string, ['titulo', 'entradilla', 'contenido'])
            found_news = Noticia.objects.filter(entry_query)[:num_results]
            last_entry['news'] = not Noticia.objects.filter(entry_query)[num_results + 1:].exists()
        if filtro == 'agenda' or filtro == '':
            entry_query = get_query(query_string, ['titulo', 'entradilla', 'contenido'])
            found_events = Agenda.objects.filter(entry_query)[:num_results]
            last_entry['events'] = not Agenda.objects.filter(entry_query)[num_results + 1:].exists()
        if filtro == 'documento' or filtro == '':
            entry_query = get_query(query_string, ['nombre', 'descripcion'])
            found_documents = Documento.objects.filter(entry_query)[:num_results]
            last_entry['documents'] = not Documento.objects.filter(entry_query)[num_results + 1:].exists()
    found_entries = {'pages': found_pages, 'news': found_news, 'events': found_events, 'documents': found_documents}
    return render(request, 'opress/search.html', {'pagina': pagina_buscar, 'arbol_paginas': Pagina.objects.get_menu(), 'filtro': filtro, 'query_string': query_string, 'found_entries': found_entries, 'page_size': num_results, 'last_entry': last_entry})

def search_more(request, filtro=""):
    query_string = ''
    found_pages = None
    found_news = None
    found_events = None
    found_documents = None
    last_entry = {'pages': False, 'news': False, 'events': False, 'documents': False}
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        offset = int(request.GET['offset'])
        last = offset + int(request.GET['page_size'])
        if filtro == 'pagina':
            entry_query = get_query(query_string, ['titulo', 'descripcion', 'menu', 'contenido'])
            found_pages = Pagina.objects.filter(entry_query)[offset:last]
            last_entry['pages'] = not Pagina.objects.filter(entry_query)[last + 1:].exists()
        if filtro == 'noticia':
            entry_query = get_query(query_string, ['titulo', 'entradilla', 'contenido'])
            found_news = Noticia.objects.filter(entry_query)[offset:last]
            last_entry['news'] = not Noticia.objects.filter(entry_query)[last + 1:].exists()
        if filtro == 'agenda':
            entry_query = get_query(query_string, ['titulo', 'entradilla', 'contenido'])
            found_events = Agenda.objects.filter(entry_query)[offset:last]
            last_entry['events'] = not Agenda.objects.filter(entry_query)[last + 1:].exists()
        if filtro == 'documento':
            entry_query = get_query(query_string, ['nombre', 'descripcion'])
            found_documents = Documento.objects.filter(entry_query)[offset:last]
            last_entry['documents'] = not Documento.objects.filter(entry_query)[last + 1:].exists()
    found_entries = {'pages': found_pages, 'news': found_news, 'events': found_events, 'documents': found_documents}
    return render(request, 'opress/search_more.html', {'filtro_mas': filtro, 'found_entries': found_entries, 'last_entry': last_entry})

@set_warning_cookie
def contact(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = MensajeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.fecha = datetime.now()
            mensaje.ip_origen = get_ip(request)
            if form.cleaned_data['tipo']:
                recipients = TipoMensaje.objects.get(pk=form.cleaned_data['tipo'].pk).destinatario
            else:
                recipients = settings.OPRESS_CONTACT_EMAIL
            mensaje.destinatario = recipients
            mensaje.save()
            subject = "Mensaje enviado por un usuario a través de la página '%s'" % request.build_absolute_uri()
            message = form.cleaned_data['texto']
            sender = form.cleaned_data['remitente']
            html_content = render(request, 'opress/email/contact.html', {'message': message, 'sender': sender, 'type': form.cleaned_data['tipo']}).content
            msg = EmailMessage(subject, html_content, settings.OPRESS_CONTACT_EMAIL, recipients.split(";"), headers={'Reply-To': sender})
            msg.content_subtype = "html"
            msg.send()
            return HttpResponseRedirect(reverse('static_page', kwargs={'slug': 'contactar/gracias'}))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = MensajeForm()
    pagina_contactar = None
    for pagina in Pagina.objects.filter(slug='contactar'):
        if pagina.get_url() == 'contactar':
            pagina.ancestros = pagina.get_ancestors()
            pagina_contactar = pagina
    return render(request, 'opress/contact.html', {'pagina': pagina_contactar, 'arbol_paginas': Pagina.objects.get_menu(), 'form': form})



@set_warning_cookie
def blog_article(request, slug, section='articulo'):
    blog = get_object_or_404(Blog, subdominio=request.subdomain)
    seccion = None
    if section == 'articulo':
        filtro_seccion = Q(seccion=None)
    else:
        #seccion = get_object_or_404(SeccionBlog, blog=blog, slug=section)
        filtro_seccion = Q(seccion__slug=section)
    articulo = get_object_or_404(Articulo, Q(inicio__lte=datetime.now()) | Q(inicio__isnull=True), filtro_seccion, blog=blog, slug=slug)
    article_list = Articulo.objects.filter(~Q(slug=slug), Q(inicio__lte=datetime.now()) | Q(inicio__isnull=True), blog=blog).order_by('-fecha')[:4]

    id_list = list(Articulo.objects.filter(Q(inicio__lte=datetime.now()) | Q(inicio__isnull=True), blog=blog).order_by('-fecha').values_list('id', flat=True))
    try:
        articulo_siguiente = None
        articulo_anterior = None
        if id_list.index(articulo.id) < len(id_list) - 1:
            articulo_siguiente = Articulo.objects.get(id=id_list[id_list.index(articulo.id) + 1])
        if id_list.index(articulo.id) > 0:
            articulo_anterior = Articulo.objects.get(id=id_list[id_list.index(articulo.id) - 1])
    except IndexError:
        pass

    articulo.contenido = articulo.contenido.replace('"/media/', '"' + settings.MEDIA_URL).replace("'/media/", "'" + settings.MEDIA_URL)
    return render(request, 'opress/blogs/article.html', {'object': articulo, 'articulo': articulo, 'articulo_siguiente': articulo_siguiente, 'articulo_anterior': articulo_anterior, 'arbol_paginas': Pagina.objects.get_menu(), 'historico': Articulo.objects.filter(Q(inicio__lte=datetime.now()) | Q(inicio__isnull=True), blog=blog, fecha__lt=datetime.now()).dates('fecha', 'year', order='DESC'), 'article_list': article_list})

@set_warning_cookie
def blog_archive(request, year):
    blog = get_object_or_404(Blog, subdominio=request.subdomain)
    article_list = Articulo.objects.filter(blog=blog, inicio__lte=datetime.now()).order_by('-fecha')
    if year:
        article_list = article_list.filter(fecha__year=year)
    paginator = Paginator(article_list, 10)
    page = request.GET.get('page')
    try:
        article_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        article_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        article_list = paginator.page(paginator.num_pages)
    return render(request, 'opress/blogs/index.html', {'blog': blog, 'arbol_paginas': Pagina.objects.get_menu(), 'article_list': article_list, 'year': year, 'historico': Articulo.objects.filter(blog=blog, inicio__lt=datetime.now()).dates('fecha', 'year', order='DESC')})

@set_warning_cookie
def blog_index(request):
    return blog_archive(request, None)

@set_warning_cookie
def error404(request):
    response = render(request, 'opress/404.html', {'arbol_paginas': Pagina.objects.get_menu(),})
    response.status_code = 404
    return response

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sites to be viewed or edited.
    """
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class NoticiaViewSet(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Noticia.objects.all()
    serializer_class = NoticiaSerializer

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer