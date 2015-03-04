# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from filesharing.models import *
from django.contrib.auth.models import Group

admin.site.register(Directory, MPTTModelAdmin)
admin.site.register(File)
admin.site.register(User)

# уберем лишнее из админки
admin.site.unregister(Group)

