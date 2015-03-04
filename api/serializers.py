from django.forms import widgets
from rest_framework import serializers
from filesharing.models import *


class DirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Directory
        fields = ('id', 'name', 'parent', 'owner')

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'name', 'parent', 'my_file')