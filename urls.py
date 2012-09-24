from django.conf.urls import patterns, url, include
from django.http import HttpResponse
from views import Index

urlpatterns = patterns('',
    url(r'^favicon\.ico/?$', lambda request: HttpResponse('AAABAAEAEBACAAEAAQCwAAAAFgAAACgAAAAQAAAAIAAAAAEAAQAAAAAAAAAA'
        'AAAAAAAAAAAAAAAAAAAAAAD///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
        content_type='image/x-icon')),
    url(r'^$', Index.as_view()),
    url(r'^', include('cms.urls')),
)
