import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

ROOT_URLCONF = 'urls'
SECRET_KEY = 'sekrit'
TEMPLATE_DIRS = ['templates']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
CMS_TEMPLATES = [('dummy.html', 'dummy.html')]
CMS_MODERATOR = False
CMS_PERMISSION = False
TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
]
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'cms',
    'mptt',
    'menus',
    'sekizai',
]
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(PROJECT_DIR, 'static')]
DEBUG = True
