# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import Http404
from subdomains.utils import reverse
from .models import Blog, Articulo, Pagina, Noticia, Agenda

FEED_COPYRIGHT = 'Copyright %s Orden de Predicadores. Todos los derechos reservados.' % datetime.now().year
FEED_TTL = 20

class BlogFeed(Feed):

    def get_object(self, request):
        return get_object_or_404(Blog, subdominio=request.subdomain)

    def title(self, obj):
        return obj.titulo

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.subtitulo

    feed_copyright = FEED_COPYRIGHT
    ttl = FEED_TTL

    def items(self, obj):
        return Articulo.objects.filter(Q(inicio__lte=datetime.now()) | Q(inicio__isnull=True), blog=obj).order_by('-fecha')[:15]

    def item_title(self, item):
        return item.titulo

    def item_description(self, item):
        return item.contenido

    def item_author_name(self, item):
        return item.blog.autor.nombre

    def item_pubdate(self, item):
        return datetime.combine(item.inicio if item.inicio else item.fecha, datetime.min.time())

class NewsFeed(Feed):

    def get_object(self, request):
        pagina_noticias = None
        for pagina in Pagina.objects.filter(slug='noticias'):
            if pagina.get_url() == 'noticias':
                pagina_noticias = pagina
        if pagina_noticias:
            return pagina_noticias
        else:
            raise Http404

    title = "Noticias de Familia Dominicana"

    def link(self, obj):
        return obj.get_absolute_url()

    description = "Últimas noticias relacionadas con la Familia Dominicana"

    feed_copyright = FEED_COPYRIGHT
    ttl = FEED_TTL

    def items(self, obj):
        return Noticia.objects.filter(fecha__lte=datetime.now()).order_by('-fecha')[:15]

    def item_title(self, item):
        return item.titulo

    def item_description(self, item):
        return item.entradilla

    def item_pubdate(self, item):
        return datetime.combine(item.fecha, datetime.min.time())

class EventsFeed(Feed):

    def get_object(self, request):
        pagina_agenda = None
        for pagina in Pagina.objects.filter(slug='agenda'):
            if pagina.get_url() == 'agenda':
                pagina_agenda = pagina
        if pagina_agenda:
            return pagina_agenda
        else:
            raise Http404

    title = "Agenda de Familia Dominicana"

    def link(self, obj):
        return obj.get_absolute_url()

    description = "Próximos eventos de la Familia Dominicana (siguientes 7 días)"

    feed_copyright = FEED_COPYRIGHT
    ttl = FEED_TTL

    def items(self, obj):
        return Agenda.objects.filter(fecha_inicio__lte=datetime.now().date() + timedelta(days=7), fecha_fin__gte=datetime.now().date()).order_by('fecha_inicio')

    def item_title(self, item):
        return item.titulo

    def item_description(self, item):
        return item.entradilla

    def item_pubdate(self, item):
        return datetime.combine(item.fecha_publicacion, datetime.min.time())
