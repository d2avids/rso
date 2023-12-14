from django.contrib import admin
from import_export.admin import ImportExportModelAdmin


from headquarters.models import (Area, CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 EducationalInstitution, LocalHeadquarter,
                                 Position, Region, RegionalHeadquarter,
                                 UserCentralHeadquarterPosition,
                                 UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition)
from headquarters.resources import RegionResource


@admin.register(CentralHeadquarter)
class CentralHeadquarterAdmin(admin.ModelAdmin):
    pass


@admin.register(DistrictHeadquarter)
class DistrictHeadquarterAdmin(admin.ModelAdmin):
    pass


@admin.register(RegionalHeadquarter)
class RegionalHeadquarterAdmin(admin.ModelAdmin):
    pass


@admin.register(LocalHeadquarter)
class LocalHeadquarterAdmin(admin.ModelAdmin):
    pass


@admin.register(EducationalHeadquarter)
class EducationalHeadquarterAdmin(admin.ModelAdmin):
    pass


@admin.register(Detachment)
class DetachmentAdmin(admin.ModelAdmin):
    pass


@admin.register(UserCentralHeadquarterPosition)
class UserCentralHeadquarterPositionAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """
        Переопределяет метод для удаления набора объектов через админ-панель.
        """
        for obj in queryset:
            obj.delete()


@admin.register(UserDistrictHeadquarterPosition)
class UserDistrictHeadquarterPositionAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """
        Переопределяет метод для удаления набора объектов через админ-панель.
        """
        for obj in queryset:
            obj.delete()


@admin.register(UserRegionalHeadquarterPosition)
class UserRegionalHeadquarterPositionAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """
        Переопределяет метод для удаления набора объектов через админ-панель.
        """
        for obj in queryset:
            obj.delete()


@admin.register(UserLocalHeadquarterPosition)
class UserLocalHeadquarterPositionAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """
        Переопределяет метод для удаления набора объектов через админ-панель.
        """
        for obj in queryset:
            obj.delete()


@admin.register(UserEducationalHeadquarterPosition)
class UserEducationalHeadquarterPositionAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """
        Переопределяет метод для удаления набора объектов через админ-панель.
        """
        for obj in queryset:
            obj.delete()


@admin.register(UserDetachmentPosition)
class UserDetachmentPositionAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """
        Переопределяет метод для удаления набора объектов через админ-панель.
        """
        for obj in queryset:
            obj.delete()


@admin.register(EducationalInstitution)
class EducationalInstAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin):
    resource_class = RegionResource


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass
