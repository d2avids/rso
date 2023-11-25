from django.contrib import admin
from headquarters.models import Region, Area, Detachment


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Detachment)
class DetachmentAdmin(admin.ModelAdmin):
    pass
