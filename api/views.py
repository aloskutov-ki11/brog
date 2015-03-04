# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics

from rest_framework.response import Response
from rest_framework import status, exceptions

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from filesharing.models import *
from api.serializers import DirectorySerializer, FileSerializer



def get_object_by_id_or_path(model=Directory, pk=None, path=None):
    if pk:
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise Http404
    if path:
        try:
            return model.objects.get_by_full_path(path)
        except model.DoesNotExist:
            raise Http404


class DirList(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        dirs = Directory.objects.all()#filter(owner=self.request.user)
        serializer = DirectorySerializer(dirs, many=True)
        return Response(serializer.data)


class DirDetail(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None, path=None, format=None):
        dir = get_object_by_id_or_path(model=Directory, pk=pk, path=path)
        if has_access(dir, self.request.user):
            serializer = DirectorySerializer(dir)
            return Response(serializer.data)
        else:
            raise exceptions.PermissionDenied()

    def post(self, request, pk=None, path=None, format=None):
        parent_dir = get_object_by_id_or_path(model=Directory, pk=pk, path=path)
        self.request.data['owner'] = self.request.user.id
        self.request.data['parent'] = parent_dir.id
        serializer = DirectorySerializer(data=self.request.data)
        if has_access(parent_dir, self.request.user):
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.PermissionDenied()


    def put(self, request, pk=None, path=None, format=None):
        dir = get_object_by_id_or_path(model=Directory, pk=pk, path=path)
        serializer = DirectorySerializer(dir, data=request.data)

        if has_access(dir, self.request.user):
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.PermissionDenied()

    def delete(self, request, pk=None, path=None, format=None):
        dir = get_object_by_id_or_path(model=Directory, pk=pk, path=path)

        if has_access(dir, self.request.user):
            dir.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.PermissionDenied()


class DirsListByParentId(generics.ListAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = DirectorySerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        cur_dir = Directory.objects.get(pk=pk)
        try:
            return Directory.objects.filter(owner=self.request.user, parent=cur_dir)
        except Directory.DoesNotExist:
            raise Http404


class DirsListByParentPath(generics.ListAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = DirectorySerializer

    def get_queryset(self):
        path = self.kwargs['path']
        cur_dir = Directory.objects.get_by_full_path(path=path)
        try:
            return Directory.objects.filter(owner=self.request.user, parent=cur_dir)
        except Directory.DoesNotExist:
            raise Http404


class FilesListByParentId(generics.ListAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = FileSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        cur_dir = Directory.objects.get(pk=pk)
        if has_access(cur_dir, self.request.user):
            try:
                return File.objects.filter(parent=cur_dir)
            except File.DoesNotExist:
                raise Http404
        else:
            raise exceptions.PermissionDenied()


class FilesListByParentPath(generics.ListAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = FileSerializer

    def get_queryset(self):
        path = self.kwargs['path']
        cur_dir = Directory.objects.get_by_full_path(path=path)
        if has_access(cur_dir, self.request.user):
            try:
                return File.objects.filter(parent=cur_dir)
            except File.DoesNotExist:
                raise Http404
        else:
            raise exceptions.PermissionDenied()

class FileDownload(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None, path=None, format=None):
        file = get_object_by_id_or_path(model=File, pk=pk, path=path)
        if has_access(file.parent, self.request.user):
            response = HttpResponse()
            response['Content-Disposition'] = "attachment; filename="+file.name
            response['X-Accel-Redirect'] = file.my_file.url
            return response
        else:
            raise exceptions.PermissionDenied()


class FileUpload(generics.CreateAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = FileSerializer

    def post(self, request, pk=None, path=None, format=None):
        cur_dir = get_object_by_id_or_path(model=Directory, pk=pk, path=path)
        self.request.data['parent'] = cur_dir.id
        serializer = FileSerializer(data=self.request.data)
        if has_access(cur_dir, self.request.user):
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.PermissionDenied()


class FileDetail(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None, path=None, format=None):
        file = get_object_by_id_or_path(model=File, pk=pk, path=path)
        if has_access(file.parent, self.request.user):
            serializer = FileSerializer(file)
            return Response(serializer.data)
        else:
            raise exceptions.PermissionDenied()

    def delete(self, request, pk=None, path=None, format=None):
        file = get_object_by_id_or_path(model=File, pk=pk, path=path)
        if has_access(file.parent, self.request.user):
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.PermissionDenied()


























