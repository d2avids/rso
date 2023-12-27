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
from headquarters.resources import (RegionResource,
                                    EducationalInstitutionResource,
                                    DistrictHeadquarterResource,
                                    RegionalHeadquarterResource)


@admin.register(CentralHeadquarter)
class CentralHeadquarterAdmin(admin.ModelAdmin):
    pass


@admin.register(DistrictHeadquarter)
class DistrictHeadquarterAdmin(ImportExportModelAdmin):
    resource_class = DistrictHeadquarterResource


@admin.register(RegionalHeadquarter)
class RegionalHeadquarterAdmin(ImportExportModelAdmin):
    resource_class = RegionalHeadquarterResource


@admin.register(LocalHeadquarter)
class LocalHeadquarterAdmin(admin.ModelAdmin):
    pass


@admin.register(EducationalHeadquarter)
class EducationalHeadquarterAdmin(admin.ModelAdmin):
    pass


@admin.register(Detachment)
class DetachmentAdmin(admin.ModelAdmin):
    pass


class BaseCentralPositionAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """
        Переопределяет метод для удаления набора объектов через админ-панель.
        """
        for obj in queryset:
            obj.delete()

    def has_add_permission(self, request, obj=None):
        """Запрещаем добавление участника в отряд через админку."""
        return False


@admin.register(UserCentralHeadquarterPosition)
class UserCentralHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    pass


@admin.register(UserDistrictHeadquarterPosition)
class UserDistrictHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    pass


@admin.register(UserRegionalHeadquarterPosition)
class UserRegionalHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    pass


@admin.register(UserLocalHeadquarterPosition)
class UserLocalHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    pass


@admin.register(UserEducationalHeadquarterPosition)
class UserEducationalHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    pass


@admin.register(UserDetachmentPosition)
class UserDetachmentPositionAdmin(BaseCentralPositionAdmin):
    def has_add_permission(self, request, obj=None):
        """Разрешаем добавление участника в отряд через админку."""
        return True


@admin.register(EducationalInstitution)
class EducationalInstAdmin(ImportExportModelAdmin):
    resource_class = EducationalInstitutionResource


@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin):
    resource_class = RegionResource


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass
