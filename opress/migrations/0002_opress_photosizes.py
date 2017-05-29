# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


def opress_initial_photosizes(apps, schema_editor):

    PhotoSize = apps.get_model('photologue', 'PhotoSize')

    # If there are already Photosizes, then we are upgrading an existing
    # installation, we don't want to auto-create some PhotoSizes.
    if PhotoSize.objects.all().count() > 3:
        return
    PhotoSize.objects.create(name='normal',
                             width=400,
                             crop=False,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='pagina_icono',
                             width=330,
                             height=207,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='pagina_cabecera',
                             width=730,
                             height=300,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='bloque_timeline',
                             width=140,
                             height=110,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='bloque_ficha',
                             width=430,
                             crop=False,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='bloque_ancho_completo',
                             width=730,
                             height=300,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='noticias_icono_portada',
                             width=300,
                             height=187,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='noticias_icono_ennoticias',
                             width=397,
                             height=250,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='noticia_imagen',
                             width=730,
                             height=300,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='noticias_relacionadas',
                             width=397,
                             height=250,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='agenda_icono',
                             width=90,
                             height=90,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='agenda_imagen',
                             width=730,
                             height=300,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='portada_destacado',
                             width=1040,
                             height=356,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='autor_foto',
                             width=90,
                             height=90,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='prensa_icono',
                             width=200,
                             height=120,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='documento_icono',
                             width=300,
                             height=187,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='bloque_icono',
                             width=300,
                             height=187,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='autor_blog_foto',
                             width=330,
                             height=207,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='autor_articulo_foto',
                             width=330,
                             height=207,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='blog_imagen',
                             width=480,
                             height=320,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)
    PhotoSize.objects.create(name='recurso_icono',
                             width=140,
                             height=140,
                             crop=True,
                             pre_cache=False,
                             increment_count=False)

class Migration(migrations.Migration):

    dependencies = [
        ('opress', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(opress_initial_photosizes),
]