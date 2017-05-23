# -*- coding: utf-8 -*-

"""
Django settings for [:SAMPLE_PROJECT:] project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, platform
from photologue import PHOTOLOGUE_APP_DIR

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '[:SECRET_KEY:]'

# SECURITY WARNING: don't run with debug turned on in production!
PRODUCTION = (platform.node() != 'desarrollo' and 'dev-' not in platform.node())
PROFILING = False
DEBUG = not PRODUCTION
APPEND_SLASH = DEBUG

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates/'),
            os.path.join(BASE_DIR, 'error/'),
            PHOTOLOGUE_APP_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'opress.context_processors.opress',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

if PRODUCTION:
    ALLOWED_HOSTS = [:PRODUCTION_ALLOWED_HOSTS:]
else:
    ALLOWED_HOSTS = [:DEBUG_ALLOWED_HOSTS:]


# Application definition

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'filebrowser',
    'photologue',
    'sortedm2m',
    'opress',
    'mptt',
    'django_mptt_admin',
    'rest_framework',
    'rest_framework.authtoken',
    'tinymce',
    'taggit',
    'taggit_labels',
    'django_statsd',
    'debug_toolbar',
)

STATSD_CLIENT = 'django_statsd.clients.normal'
STATSD_PREFIX = '[:SAMPLE_PROJECT:].env'
STATSD_HOST = 'localhost'
STATSD_PORT = 8125
STATSD_MODEL_SIGNALS = True

#INTERNAL_IPS = ('192.168.31.11',)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
   'PAGINATE_BY': 10,
}

MIDDLEWARE_CLASSES = (
    'NginxMemCacheMiddleWare.NginxMemCacheMiddleWare',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CONN_MAX_AGE = 10

if PROFILING:
    MIDDLEWARE_CLASSES = (
        'opress.middleware.ProfileMiddleware',
    ) + MIDDLEWARE_CLASSES
else:
    if PRODUCTION:
        MIDDLEWARE_CLASSES = (
            'NginxMemCacheMiddleWare.NginxMemCacheMiddleWare',
        ) + MIDDLEWARE_CLASSES
        CACHE_KEY_PREFIX = '/[:SAMPLE_PROJECT:]'
        CACHE_IGNORE_REGEXPS = (
            r'/admin.*',
        )

STATSD_PATCHES = [
    'django_statsd.patches.db',
    'django_statsd.patches.cache',
]

ROOT_URLCONF = '[:SAMPLE_PROJECT:].urls'

WSGI_APPLICATION = '[:SAMPLE_PROJECT:].wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

if PRODUCTION:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '[:SAMPLE_PROJECT:]',
            'HOST': '172.16.0.1',
            'USER': '[:SAMPLE_PROJECT:]',
            'PASSWORD': '[:PRODUCTION_DB_PASSWORD:]',
            'OPTIONS': {'charset': 'utf8mb4', 'init_command':'SET character_set_connection=utf8mb4, collation_connection=utf8mb4_spanish_ci'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '[:SAMPLE_PROJECT:]',
            'HOST': 'localhost',
            'USER': '[:SAMPLE_PROJECT:]',
            'PASSWORD': '[:DEBUG_DB_PASSWORD:]',
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 2

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = '[:PROJECT_DIR:]/static/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
ADMIN_URL = '/admin'
MEDIA_ROOT = '[:PROJECT_DIR:]/media/'

LOCALE_PATHS = (
    '[:PROJECT_DIR:]/locale',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

CACHE_KEY_PREFIX = '/[:SAMPLE_PROJECT:]'
CACHE_IGNORE_REGEXPS = (
    r'/admin.*',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 60*60*3,
        'KEY_PREFIX': CACHE_KEY_PREFIX,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '[:SAMPLE_PROJECT:].log'),
            'maxBytes': 1024*1024*15, # 15MB
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
        },
        '[:SAMPLE_PROJECT:]': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

GRAPPELLI_ADMIN_TITLE = '[:PROJECT_TITLE:]'
GRAPPELLI_INDEX_DASHBOARD = '[:SAMPLE_PROJECT:].dashboard.CustomIndexDashboard'

OPRESS_COOKIES_URL = 'privacidad-y-cookies'
#OPRESS_PAGES_ICON_SIZE_LABEL = '(300x200px)'
#OPRESS_PAGES_ICON_SIZE = 'page_icon'
OPRESS_IMAGE_SIZES = {
    'Normal': ('Normal', '400px de ancho'),
    'pagina_icono': ('pagina_icono', '330x207px'),
    'pagina_cabecera': ('pagina_cabecera', '730x300px'),
    'bloque_timeline': ('bloque_timeline', '140x110px'),
    'bloque_ficha': ('bloque_ficha', '430px de ancho'),
    'bloque_ancho_completo': ('bloque_ancho_completo', '730x300px'),
    'noticias_icono_portada': ('noticias_icono_portada', '300x187px'),
    'noticias_icono_ennoticias': ('noticias_icono_ennoticias', '397x250px'),
    'noticia_imagen': ('noticia_imagen', '730x300px de ancho'),
    'noticias_relacionadas': ('noticias_relacionadas', '397x250px'),
    'agenda_icono': ('agenda_icono', '90x90px'),
    'agenda_imagen': ('agenda_imagen', '730x300px'),
    'portada_destacado': ('portada_destacado', '1040x356px'),
    'autor_foto': ('autor_foto', '90x90px'),
    'prensa_icono': ('prensa_icono', '200x120px'),
    'documento_icono': ('documento_icono', '300x187px'),
    'bloque_icono': ('documento_icono', '300x187px'),
    'autor_blog_foto': ('autor_blog_foto', '330x207px'),
    'autor_articulo_foto': ('autor_articulo_foto', '330x207px'),
    'blog_imagen': ('blog_imagen', u'480x320px'),
    'otro_blog_imagen': ('otro_blog_imagen', u'152x140px'),
    'recurso_icono': ('recurso_icono', u'tamaño variable'),
}
if PRODUCTION:
    OPRESS_CONTACT_EMAIL = '[:OPRESS_CONTACT_EMAIL:]'
else:
    OPRESS_CONTACT_EMAIL = 'alan@dominicos.org'
OPRESS_CACHE_UPDATE = []

FILEBROWSER_EXTENSIONS = {
    'Folder': [''],
    'Document': ['.pdf','.doc','.docx','.rtf','.txt','.xls','.csv'],
}
FILEBROWSER_SELECT_FORMATS = {
    'file': ['Folder','Document',],
    'document': ['Document'],
}

TAGGIT_CASE_INSENSITIVE = True

TINYMCE_FILEBROWSER=True
TINYMCE_DEFAULT_CONFIG = {
    'mode': "specific_textareas",
    'editor_selector': "mceEditor",
    'theme': 'advanced',
    'skin': 'grappelli',
    'accessibility_warnings': False,
    'browsers': 'gecko,msie,safari,opera',
    'dialog_type': 'modal',
    'editor_deselector': 'mceNoEditor',
    'keep_styles': False,
    'language': 'es',
    'object_resizing': False,
    'plugins': 'advimage,advlink,fullscreen,paste,table,media,searchreplace,grappelli,template,youtube,gallerycon,inlinepopups',
    'jquery_url': STATIC_URL + 'grappelli/jquery/jquery-1.9.1.min.js',
    'content_css': STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/plugins/gallerycon/css/tiny-mce-extra.css',
    # 'directionality' : "rtl",
    'file_browser_callback': 'CustomFileBrowser',
    'gallerycon_settings':
    {
        'urls':
        {
            'galleries': ADMIN_URL + '/opress/galleries?format=json&jsoncallback=?',
            'images': ADMIN_URL + '/opress/images/{gallery_id}?format=json&jsoncallback=?',
            'image': ADMIN_URL + '/opress/image/{image_id}?format=json&jsoncallback=?',
            'img_src': ADMIN_URL + '/opress/image_src/{image_id}/{size_id}?format=json&jsoncallback=?'
        },
        'sizes':
        [
            {
                'id': 'Icono',
                'name': 'Icono'
            },
            {
                'id': 'Normal',
                'name': 'Normal'
            },
        ],
        'default_size': 'Normal',
        'default_alignment': 'left'
    },

    # Cleanup/Output
    'element_format': 'xhtml',
    'fix_list_elements': True,
    'forced_root_block': 'p',
    'style_formats': [
        {'title': 'Paragraph Small', 'block': 'p', 'classes': 'p_small'},
        {'title': 'Paragraph ImageCaption', 'block': 'p', 'classes': 'p_caption'},
        {'title': 'Clearfix', 'block': 'p', 'classes': 'clearfix'},
        {'title': 'Code', 'block': 'p', 'classes': 'code'}
    ],
    'verify_html': True,
    # URL
    'relative_urls': False,
    'remove_script_host': True,
    # Layout
    'width': 758,
    'height': 300,
    'indentation': '10px',
    # Theme Advanced
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_toolbar_align': 'left',
    'theme_advanced_statusbar_location': 'bottom',
    'theme_advanced_buttons1': 'formatselect,styleselect,|,bold,italic,underline,|,bullist,numlist,blockquote,outdent,indent,|,justifyleft,justifycenter,justifyright,justifyfull,|,,grappelli_adv',
    'theme_advanced_buttons2': 'search,|,undo,redo,|,link,unlink,|,gallerycon,|,fullscreen,|,pasteword,youtube,charmap,|,code,|,table,cleanup,grappelli_documentstructure',
    'theme_advanced_buttons3': '',
    'theme_advanced_path': False,
    'theme_advanced_blockformats': 'p,h1,h2,h3,h4,pre',
    'theme_advanced_resizing': True,
    'theme_advanced_resize_horizontal': False,
    'theme_advanced_resizing_use_cookie': True,
    # Image Plugin
    # see http://www.tinymce.com/wiki.php/Plugin:advimage
    'theme_advanced_styles': 'Image Left=img_left;Image Right=img_right;Image Block=img_block',
    'advimage_update_dimensions_onchange': True,
    # Link Settings
    # see http://www.tinymce.com/wiki.php/Plugin:advlink
    'advlink_styles': 'Internal Link=internal;External Link=external',
    # Media Plugin
    # see http://www.tinymce.com/wiki.php/Plugin:media
    'media_strict': True,
    # Grappelli Settings
    'grappelli_adv_hidden': False,
    'grappelli_show_documentstructure': False
}
