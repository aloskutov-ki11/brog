# -*- coding: utf-8 -*-
from django import forms
from filesharing.models import Directory, File


class CreateDirectoryForm(forms.ModelForm):
    class Meta(object):
        model = Directory
        fields = ['name']


class UploadFileForm(forms.ModelForm):
    class Meta(object):
        model = File
        fields = ['my_file']


class UpdateDirectoryNameForm(forms.ModelForm):
    class Meta(object):
        model = Directory
        fields = ['name']
