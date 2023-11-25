from django.contrib import admin

from headquarters.models import (Area, CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, Region, EducationalInstitution)


@admin.register(EducationalInstitution)
class EducationalInstAdmin(admin.ModelAdmin):
    pass


@admin.register(CentralHeadquarter)
class CentralAdmin(admin.ModelAdmin):
    pass


@admin.register(DistrictHeadquarter)
class DistrictAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Detachment)
class DetachmentAdmin(admin.ModelAdmin):
    pass
