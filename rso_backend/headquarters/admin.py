from django.contrib import admin
from django.core.exceptions import ValidationError
from import_export.admin import ImportExportModelAdmin

from headquarters.forms import (CentralForm, DetachmentForm, DistrictForm,
                                EducationalForm, LocalForm, RegionalForm)
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
from headquarters.resources import (DistrictHeadquarterResource,
                                    EducationalInstitutionResource,
                                    RegionalHeadquarterResource,
                                    RegionResource)


class BaseUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'commander', 'city',)
    search_fields = ('name', 'city')


@admin.register(CentralHeadquarter)
class CentralHeadquarterAdmin(BaseUnitAdmin):
    form = CentralForm


@admin.register(DistrictHeadquarter)
class DistrictHeadquarterAdmin(ImportExportModelAdmin):
    resource_class = DistrictHeadquarterResource
    list_display = ('id', 'name', 'commander', 'city',)
    search_fields = ('name', 'city')
    form = DistrictForm


@admin.register(RegionalHeadquarter)
class RegionalHeadquarterAdmin(ImportExportModelAdmin):
    resource_class = RegionalHeadquarterResource
    list_display = ('id', 'name', 'commander', 'city',)
    search_fields = ('name', 'city')
    form = RegionalForm


@admin.register(LocalHeadquarter)
class LocalHeadquarterAdmin(BaseUnitAdmin):
    form = LocalForm


@admin.register(EducationalHeadquarter)
class EducationalHeadquarterAdmin(BaseUnitAdmin):
    form = EducationalForm


@admin.register(Detachment)
class DetachmentAdmin(BaseUnitAdmin):
    form = DetachmentForm

    def save_model(self, request, obj, form, change):
        """
        Валидируем создание отряда с регионом несуществующего РШ.
        """
        if (not obj.regional_headquarter and
                not RegionalHeadquarter.objects.filter(
                    region=obj.region).exists()
        ):
            raise ValidationError({
                'region': 'В базе данных не найден РШ '
                          'с данным регионом. '
                          'Для начала создайте соответсвующий РШ или выберите '
                          'другой регион.'
            })

        super().save_model(request, obj, form, change)


class BaseCentralPositionAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'headquarter',)

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
    search_fields = ('name',)
    resource_class = EducationalInstitutionResource


@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')
    resource_class = RegionResource


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
