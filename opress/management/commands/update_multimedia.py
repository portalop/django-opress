# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand
from opress.models import Multimedia, ProveedorMultimedia
from django.utils import dateparse
import decimal
from datetime import datetime, date
from apiclient.discovery import build
import flickr_api
from flickr_api import Photo
import soundcloud

class Command(BaseCommand):
    help = 'Actualiza la caché de multimedia desde las APIs'

    def add_arguments(self, parser):
        parser.add_argument('num_videos', type=int)

    def get_soundcloud_duration(self, duracion):
        #num_seconds = decimal.Decimal(duracion) // 1000
        num_seconds = duracion // 1000
        str_duracion = ''
        if num_seconds >= 3600:
            str_duracion = '%s h ' % (num_seconds // 3600)
            num_seconds = num_seconds % 3600
        if num_seconds >= 60:
            str_duracion = str_duracion + '%s m ' % (num_seconds // 60)
            num_seconds = num_seconds % 60
        if num_seconds > 0:
            str_duracion = str_duracion + '%s s' % num_seconds
        return str.rstrip(str_duracion)

    def get_youtube_duration(self, duracion):
        return duracion.replace('PT', '').replace('H', 'h ').replace('M', 'm ').replace('S', 's ').rstrip()

    def update_youtube(self, num_videos):
        YOUTUBE_API_SERVICE_NAME = 'youtube'
        YOUTUBE_API_VERSION = 'v3'
        resultados_por_pagina = 0
        pagina_actual = None
        proveedor_youtube = ProveedorMultimedia.objects.get(nombre='Youtube')
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION)
        channels_response = youtube.channels().list(
            id=proveedor_youtube.identificador,
            part='contentDetails',
            key=proveedor_youtube.clave).execute()
        for channel in channels_response['items']:
            uploads_list_id = channel['contentDetails']['relatedPlaylists']['uploads']
            while num_videos > resultados_por_pagina:
                videos_list_ids = []
                playlistitems_list_request = youtube.playlistItems().list(
                    playlistId=uploads_list_id,
                    part='snippet',
                    maxResults=(10 if num_videos > 10 else num_videos),
                    key=proveedor_youtube.clave,
                    pageToken=pagina_actual
                )
                playlistitems_list_response = playlistitems_list_request.execute()
                resultados_por_pagina = playlistitems_list_response['pageInfo']['resultsPerPage']
                num_videos -= len(playlistitems_list_response['items'])
                if 'nextPageToken' in playlistitems_list_response:
                    pagina_actual = playlistitems_list_response['nextPageToken']
                else:
                    pagina_actual = None
                print '%s resultados, %s por página' % (playlistitems_list_response['pageInfo']['totalResults'], playlistitems_list_response['pageInfo']['resultsPerPage'])
                for playlist_item in playlistitems_list_response['items']:
                    videos_list_ids.append(playlist_item['snippet']['resourceId']['videoId'])

                print videos_list_ids
                videos_list_response = youtube.videos().list(
                    id=', '.join(videos_list_ids),
                    part='contentDetails, snippet',
                    key=proveedor_youtube.clave
                ).execute()
                for video in videos_list_response['items']:
                    youtube_video, creado = Multimedia.objects.get_or_create(identificador=video['id'], proveedor=proveedor_youtube)
                    if creado or youtube_video.titulo != video['snippet']['title'] or youtube_video.descripcion != video['snippet']['description'] or youtube_video.duracion != self.get_youtube_duration(video['contentDetails']['duration']) or youtube_video.icono != video['snippet']['thumbnails']['high']['url']:
                        print '%s (%s)' % (video['snippet']['title'], video['contentDetails']['duration'])
                        youtube_video.identificador = video['id']
                        youtube_video.titulo = video['snippet']['title']
                        youtube_video.descripcion = video['snippet']['description']
                        youtube_video.duracion = self.get_youtube_duration(video['contentDetails']['duration'])
                        youtube_video.icono = video['snippet']['thumbnails']['high']['url']
                        youtube_video.fecha = dateparse.parse_datetime(video['snippet']['publishedAt'])
                        youtube_video.save()

    def update_flickr(self, num_albumes):
        proveedor_flickr = ProveedorMultimedia.objects.get(nombre='Flickr')
        flickr_api.set_keys(api_key=proveedor_flickr.clave, api_secret=proveedor_flickr.identificador)
        user = flickr_api.Person.findByUserName('Dominicos OP')
        for album in user.getPhotosets()[:num_albumes]:
            flickr_album, creado = Multimedia.objects.get_or_create(identificador=album.id, proveedor=proveedor_flickr)
            fecha = date.fromtimestamp(int(album['date_create']))
            if creado or flickr_album.titulo != album.title or flickr_album.descripcion != album.description or flickr_album.fecha != fecha:
                flickr_album.titulo = album.title
                flickr_album.icono = Photo(id=album['primary']).getSizes()['Small 320']['source']
                flickr_album.descripcion = album.description
                flickr_album.fecha = fecha
                flickr_album.save()

    def update_soundcloud(self, num_sonidos):
        proveedor_soundcloud = ProveedorMultimedia.objects.get(nombre='Soundcloud')
        client = soundcloud.Client(client_id=proveedor_soundcloud.clave)
        tracks = client.get('/users/%s/tracks' % proveedor_soundcloud.identificador, limit=num_sonidos)
        for track in tracks:
            soundcloud_track, creado = Multimedia.objects.get_or_create(identificador=track.id, proveedor=proveedor_soundcloud)
            fecha = datetime.strptime(track.created_at[:-6], '%Y/%m/%d %H:%M:%S')
            if creado or soundcloud_track.titulo != track.title or soundcloud_track.descripcion != track.description or soundcloud_track.fecha != fecha or soundcloud_track.duracion != self.get_soundcloud_duration(track.duration):
                soundcloud_track.titulo = track.title
                soundcloud_track.descripcion = track.description
                soundcloud_track.fecha = fecha
                soundcloud_track.icono = track.artwork_url.replace('-large', '-t300x300')
                soundcloud_track.duracion = self.get_soundcloud_duration(track.duration)
                soundcloud_track.save()

    def handle(self, *args, **options):
        self.update_youtube(options['num_videos'])
        self.update_flickr(options['num_videos'])
        self.update_soundcloud(options['num_videos'])