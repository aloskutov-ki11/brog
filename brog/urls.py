# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin

# TEMP для просомтра загруженных файлов
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

admin.autodiscover()

from brog.views import *
from filesharing.views import *
from api.views import *

urlpatterns = patterns('',

    url(r'^', include('api.urls')),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', index),
    url(r'^accounts/profile/$', TemplateView.as_view(template_name='profile.html')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/file/path=(?P<path>.+)$', DirFileCreate.as_view(form_class=UploadFileForm)),
    url(r'^create/dir/path=(?P<path>.+)$', DirFileCreate.as_view(form_class=CreateDirectoryForm)),
    url(r'^update/dir/path=(?P<path>.+)$', DirUpdate.as_view(form_class=UpdateDirectoryNameForm)),
    url(r'^delete/dir/path=(?P<path>.+)$', DirDelete.as_view()),
    url(r'(?P<path>.+)/$', FilesView.as_view()),

)

urlpatterns = format_suffix_patterns(urlpatterns)

# TEMP для просмотра загруженных файлов
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
