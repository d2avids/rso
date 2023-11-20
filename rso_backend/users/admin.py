from django.contrib import admin

from .models import Area, Detachment, Profile, Region

admin.site.register(Profile)
admin.site.register(Region)
admin.site.register(Area)
admin.site.register(Detachment)