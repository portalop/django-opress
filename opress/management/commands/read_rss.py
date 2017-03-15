# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.db import transaction
from opress.models import OtroBlog, OtroArticulo
from opress.signals import delete_cache
import feedparser, dateparser
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Actualiza la caché de multimedia desde las APIs'

    def handle(self, *args, **options):
        for blog in OtroBlog.objects.exclude(tipo=1):
            blog_rss = feedparser.parse(blog.rss)
            with transaction.atomic():
                OtroArticulo.objects.filter(blog=blog).delete()
                for post in blog_rss.entries[:2]:
                    #print(post)
                    try:
                        fecha = dateparser.parse(post.published)
                    except AttributeError:
                        fecha = None
                    try:
                        imagen = post.media_thumbnail[0]['url']
                    except (AttributeError, IndexError, KeyError):
                        imagen=None
                    descripcion = getattr(post, 'description', None)
                    if descripcion:
                        descripcion = ''.join([p.prettify() for p in BeautifulSoup(descripcion).find_all('p')[:2]])
                    blog.otroarticulo_set.create(
                        titulo=post.title,
                        fecha=fecha,
                        url=post.link,
                        guid=getattr(post, 'id', post.link),
                        autor=getattr(post, 'author', None),
                        subtitulo=getattr(post, 'subtitle', None),
                        descripcion=descripcion,
                        imagen=imagen
                    )