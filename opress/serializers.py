from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.files import File
from django.conf import settings
from .models import Noticia, Agenda, Bloque, LocationTag, FlickrUser, Timeline, TimelineItem, PuntoGoogleMap, GoogleMap, IPUser
from .utils import get_ip_address
from rest_framework import serializers
from photologue.models import Photo
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO
import os
import logging
import requests
import cStringIO


def get_serialized_image(url):
    result = requests.get(url, verify=False)
    name = os.path.basename(url)
    file = File(BytesIO(result.content))
    return (name, file)


def get_image_from_url(data):
    try:
        image = Photo.objects.get(slug=data['slug'])
    except Photo.DoesNotExist:
        url = data.pop('image', None)
        name, file = get_serialized_image(url)
        del data['sites']
        image = Photo(**data)
        image.image.save(name, file, save=True)
        image.save()
    return image


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'groups')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name')


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ('name', 'domain')


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.URLField()

    def validate_image(self, value):
        a = requests.get(value, verify=False)
        if a.status_code != 200:
            raise serializers.ValidationError('The url is wrong.')
        file = cStringIO.StringIO(a.content)
        try:
            img = Image.open(file)
            img.close()
        except IOError:
            raise serializers.ValidationError('The file is not an image.')
        return value

    def to_representation(self, instance):
        representation = super(PhotoSerializer, self).to_representation(instance)
        representation['image'] = settings.MY_DOMAIN + settings.MEDIA_URL + representation['image']
        return representation

    class Meta:
        model = Photo
        fields = ('title', 'slug', 'caption', 'image', 'date_added', 'date_taken', 'view_count', 'crop_from', 'effect', 'is_public', 'sites')


class FlickrUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlickrUser
        fields = ('user_id', 'nombre')


class TimelineItemSerializer(serializers.ModelSerializer):
    imagen = PhotoSerializer(allow_null=True)

    class Meta:
        model = TimelineItem
        fields = ('fecha', 'titulo', 'contenido', 'imagen')


class TimelineSerializer(serializers.ModelSerializer):
    items = TimelineItemSerializer(source='timelineitem_set', many=True)

    class Meta:
        model = Timeline
        fields = ('nombre', 'orientacion', 'autoplay', 'items')


class GoogleMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleMap
        fields = ('nombre', 'codigo')


class PuntoGoogleMapSerializer(serializers.ModelSerializer):
    mapa = GoogleMapSerializer(allow_null=True)

    class Meta:
        model = PuntoGoogleMap
        fields = ('nombre', 'enlace', 'mapa', 'tipo')


class BloqueSerializer(serializers.ModelSerializer):
    icono = PhotoSerializer(allow_null=True)
    imagen = PhotoSerializer(allow_null=True)
    flickr_user = FlickrUserSerializer(allow_null=True)
    timeline = TimelineSerializer(allow_null=True)
    mapa = PuntoGoogleMapSerializer(allow_null=True)

    class Meta:
        model = Bloque
        fields = ('tipo', 'titulo', 'imagen', 'enlace', 'contenido', 'flickr_user', 'flickr_album', 'icono', 'youtube_id', 'timeline', 'mapa', 'se_hereda', 'grupo')


class NoticiaSerializer(serializers.ModelSerializer):
    icono = PhotoSerializer(allow_null=True)
    imagen = PhotoSerializer(allow_null=True)
    bloques = BloqueSerializer(source='bloque_set', many=True)

    def create(self, validated_data):
        ip_addr = get_ip_address(self.context.get('request'))
        user = self.context.get('request').user
        publicar = IPUser.objects.get(ip_addr=ip_addr, user=user).publish
        logger = logging.getLogger("django")
        logger.debug("datos validados: %s" % validated_data)
        imagen_data = validated_data.pop('imagen', None)
        icono_data = validated_data.pop('icono', None)
        icono = None
        imagen = None
        if icono_data:
            icono = get_image_from_url(icono_data)
        if imagen_data:
            imagen = get_image_from_url(imagen_data)
        bloques = validated_data.pop('bloque_set', None)
        noticia = Noticia.objects.create(icono=icono, imagen=imagen, publicado=publicar, **validated_data)
        for bloque in bloques:
            icono_data = bloque.pop('icono', None)
            imagen_data = bloque.pop('imagen', None)
            flickr_user_data = bloque.pop('flickr_user', None)
            timeline_data = bloque.pop('timeline', None)
            mapa_data = bloque.pop('mapa', None)
            icono = None
            imagen = None
            flickr_user = None
            timeline = None
            mapa = None
            if icono_data:
                icono = get_image_from_url(icono_data)
            if imagen_data:
                imagen = get_image_from_url(imagen_data)
            if flickr_user_data:
                flickr_user, created = FlickrUser.objects.get_or_create(user_id=flickr_user_data['user_id'], nombre=flickr_user_data['nombre'])
            if timeline_data:
                items = timeline_data.pop('timelineitem_set', None)
                timeline = Timeline.objects.create(**timeline_data)
                for item in items:
                    imagen_item_data = item.pop('imagen', None)
                    imagen_item = None
                    if imagen_item_data:
                        imagen_item = get_image_from_url(imagen_item_data)
                    TimelineItem.objects.create(timeline=timeline, imagen=imagen_item, **item)
            if mapa_data:
                mapa_google_data = mapa_data.pop('mapa', None)
                mapa_google = None
                if mapa_google_data:
                    mapa_google, created = GoogleMap.objects.get_or_create(nombre=mapa_google_data['nombre'], codigo=mapa_google_data['codigo'])
                mapa_data['mapa'] = mapa_google
                mapa = PuntoGoogleMap.objects.create(**mapa_data)
            Bloque.objects.create(icono=icono, imagen=imagen, flickr_user=flickr_user, timeline=timeline, mapa=mapa, noticia=noticia, **bloque)
        return noticia

    def to_representation(self, instance):
        representation = super(NoticiaSerializer, self).to_representation(instance)
        contenido = BeautifulSoup(representation['contenido'])
        for img in contenido.findAll('img'):
            if not img['src'].startswith('http'):
                img['src'] = settings.MY_DOMAIN + img['src']
        representation['contenido'] = str(contenido)
        return representation

    class Meta:
        model = Noticia
        fields = ('titulo', 'slug', 'fecha', 'entradilla', 'icono', 'imagen', 'contenido', 'bloques')


class AgendaSerializer(TaggitSerializer, serializers.ModelSerializer):
    icono = PhotoSerializer(allow_null=True)
    imagen = PhotoSerializer(allow_null=True)
    localidad = TagListSerializerField()

    def create(self, validated_data):
        ip_addr = get_ip_address(self.context.get('request'))
        user = self.context.get('request').user
        publicar = IPUser.objects.get(ip_addr=ip_addr, user=user).publish
        logger = logging.getLogger("django")
        logger.debug("datos validados: %s" % validated_data)
        imagen_data = validated_data.pop('imagen', None)
        icono_data = validated_data.pop('icono', None)
        icono = None
        imagen = None
        if icono_data:
            icono = get_image_from_url(icono_data)
        if imagen_data:
            imagen = get_image_from_url(imagen_data)
        localidades = validated_data.pop('localidad', None)
        agenda = Agenda.objects.create(icono=icono, imagen=imagen, publicado=publicar, **validated_data)
        for localidad in localidades:
            tag, created = LocationTag.objects.get_or_create(name=localidad)
            agenda.localidad.add(tag)
        return agenda

    def to_representation(self, instance):
        representation = super(AgendaSerializer, self).to_representation(instance)
        contenido = BeautifulSoup(representation['contenido'])
        for img in contenido.findAll('img'):
            if not img['src'].startswith('http'):
                img['src'] = settings.MY_DOMAIN + img['src']
        representation['contenido'] = str(contenido)
        return representation

    class Meta:
        model = Agenda
        fields = ('titulo', 'slug', 'fecha_inicio', 'fecha_fin', 'entradilla', 'icono', 'imagen', 'contenido', 'se_anuncia', 'inicio_anuncio', 'fin_anuncio',
                  'es_periodico', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo', 'fecha_publicacion', 'localidad')
