from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from .models import Noticia
from rest_framework import serializers
from photologue.models import Photo, PHOTOLOGUE_DIR
import requests
import shutil
import logging

def get_serialized_image(imagen, url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(imagen.image.storage.path(os.path.join(PHOTOLOGUE_DIR, 'photos')), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
            return f.name

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
    class Meta:
        model = Photo
        fields = ('title', 'slug', 'caption', 'image', 'date_added', 'date_taken', 'view_count', 'crop_from', 'effect', 'is_public', 'sites')

class NoticiaSerializer(serializers.ModelSerializer):
    icono_url = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    icono = PhotoSerializer()
    imagen = PhotoSerializer()
    def create(self, validated_data):
        logger = logging.getLogger("django")
        logger.debug("datos validados: %s" % validated_data)
        imagen_data = validated_data.pop('imagen', None)
        icono_data = validated_data.pop('icono', None)
        icono, imagen = None, None
        if icono_data:
            icono = Photo.objects.create(**icono_data)
            icono.image.url = get_serialized_image(icono, validated_data.pop('icono_url'))
            icono.save()
        if imagen_data:
            imagen = Photo.objects.create(**imagen_data)
            imagen.image.url = get_serialized_image(imagen, validated_data.pop('imagen_url'))
            imagen.save()
        noticia = Noticia.objects.create(icono=icono, imagen=imagen, **validated_data)
        return noticia
    def get_icono_url(self, obj):
        return "http://%s%s" % (Site.objects.get_current().domain.split('/')[0], obj.icono.image.url)
    def get_imagen_url(self, obj):
        return "http://%s%s" % (Site.objects.get_current().domain.split('/')[0], obj.imagen.image.url)
    class Meta:
        model = Noticia
        fields = ('titulo', 'slug', 'fecha', 'entradilla', 'icono', 'imagen', 'contenido', 'icono_url', 'imagen_url')
        #depth = 1