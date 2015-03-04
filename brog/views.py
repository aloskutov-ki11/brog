# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader, RequestContext

def index(request):
    return render_to_response('index.html', RequestContext(request))

def home(request):
    return render_to_response('home.html', RequestContext(request))