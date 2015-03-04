# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from api.views import *

urlpatterns = patterns('',
    url(r'^api/dir/id/(?P<pk>[0-9]+)/$', DirDetail.as_view()),              # получить директрию по id (методы get, put, delete, post)
    url(r'^api/dir/path=(?P<path>.+)/$', DirDetail.as_view()),              # получить директорию по полному пути (методы get, put, delete, post)

    url(r'^api/get/dirs/$', DirList.as_view()),                                 # все директории пользователя
    url(r'^api/get/dirs/id/(?P<pk>[0-9]+)/$', DirsListByParentId.as_view()),    # список директорий по Id родителя
    url(r'^api/get/dirs/path=(?P<path>.+)$', DirsListByParentPath.as_view()),   # список директорйи по полному пути родителя


    url(r'^api/file/id/(?P<pk>[0-9]+)/$', FileDetail.as_view()),              # получить файл по id родителя (методы get, put, delete, post)
    url(r'^api/file/path=(?P<path>.+)/$', FileDetail.as_view()),              # получить файл по полному пути родителя (методы get, put, delete, post)

    url(r'^api/file/upload/id/(?P<pk>[0-9]+)/$', FileUpload.as_view()),              # загрузить файл в директорию с указанным id
    url(r'^api/file/upload/path=(?P<path>.+)/$', FileUpload.as_view()),              # загрузить файл в директорию с указанным полным путем

    url(r'^api/file/download/id/(?P<pk>[0-9]+)/$', FileDownload.as_view()),              # скачать файл по id
    url(r'^api/file/download/path=(?P<path>.+)/$', FileDownload.as_view()),              # скачать файл по полному пути

    url(r'^api/get/files/id/(?P<pk>[0-9]+)/$', FilesListByParentId.as_view()),    # список файлов по Id родителя
    url(r'^api/get/files/path=(?P<path>.+)/$', FilesListByParentPath.as_view()),   # список файлов по полному пути родителя
)

