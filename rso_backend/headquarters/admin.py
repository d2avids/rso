from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from import_export.admin import ImportExportModelAdmin
from django.contrib import messages

from headquarters.forms import (CentralForm, CentralPositionForm,
                                DetachmentForm, DetachmentPositionAddForm,
                                DetachmentPositionForm, DistrictForm,
                                DistrictPositionForm, EducationalForm,
                                EducationalPositionForm, LocalForm,
                                LocalPositionForm, RegionalForm,
                                RegionalPositionForm)
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

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    form.add_error(field, error)
                self.message_user(request,
                                  f"Возникли ошибки при "
                                  f"сохранении: {','.join(errors)}",
                                  level=messages.ERROR)


@admin.register(CentralHeadquarter)
class CentralHeadquarterAdmin(BaseUnitAdmin):
    form = CentralForm


@admin.register(DistrictHeadquarter)
class DistrictHeadquarterAdmin(ImportExportModelAdmin):
    resource_class = DistrictHeadquarterResource
    list_display = ('id', 'name', 'commander', 'founding_date', 'city',)
    search_fields = ('name', 'city', 'founding_date',)
    form = DistrictForm


@admin.register(RegionalHeadquarter)
class RegionalHeadquarterAdmin(ImportExportModelAdmin):
    resource_class = RegionalHeadquarterResource
    list_display = (
        'id',
        'name',
        'commander',
        'region',
        'conference_date',
        'founding_date',
        'district_headquarter',
        'city',
    )
    search_fields = (
        'name',
        'city',
        'district_headquarter__name',
        'region__name',
        'founding_date',
    )
    form = RegionalForm
    list_filter = ('district_headquarter',)


@admin.register(LocalHeadquarter)
class LocalHeadquarterAdmin(BaseUnitAdmin):
    list_display = (
        'id',
        'name',
        'commander',
        'regional_headquarter',
        'founding_date',
        'city',
    )
    list_filter = ('regional_headquarter',)
    search_fields = (
        'name', 'city', 'founding_date', 'regional_headquarter__name'
    )
    form = LocalForm


@admin.register(EducationalHeadquarter)
class EducationalHeadquarterAdmin(BaseUnitAdmin):
    list_display = (
        'id',
        'name',
        'commander',
        'local_headquarter',
        'regional_headquarter',
        'educational_institution',
        'founding_date',
        'city',
    )
    list_filter = ('local_headquarter', 'regional_headquarter',)
    search_fields = (
        'name',
        'city',
        'educational_institution__name',
        'regional_headquarter__name',
        'founding_date'
    )
    form = EducationalForm


@admin.register(Detachment)
class DetachmentAdmin(BaseUnitAdmin):
    list_display = (
        'id',
        'name',
        'commander',
        'educational_headquarter',
        'local_headquarter',
        'regional_headquarter',
        'region',
        'educational_institution',
        'area',
        'founding_date',
        'city',
    )
    list_filter = (
        'area',
        'educational_headquarter',
        'local_headquarter',
        'regional_headquarter',
    )
    search_fields = (
        'name',
        'city',
        'educational_headquarter__name',
        'local_headquarter__name',
        'region__name',
        'educational_institution__name',
    )
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
    list_filter = ('headquarter',)
    search_fields = ('user__username', 'name')

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
    form = CentralPositionForm


@admin.register(UserDistrictHeadquarterPosition)
class UserDistrictHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    form = DistrictPositionForm


@admin.register(UserRegionalHeadquarterPosition)
class UserRegionalHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    form = RegionalPositionForm


@admin.register(UserLocalHeadquarterPosition)
class UserLocalHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    form = LocalPositionForm


@admin.register(UserEducationalHeadquarterPosition)
class UserEducationalHeadquarterPositionAdmin(BaseCentralPositionAdmin):
    form = EducationalPositionForm


@admin.register(UserDetachmentPosition)
class UserDetachmentPositionAdmin(BaseCentralPositionAdmin):
    form = DetachmentPositionForm
    add_form = DetachmentPositionAddForm

    def has_add_permission(self, request, obj=None):
        """Разрешаем добавление участника в отряд через админку."""
        return True

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during position creation.
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


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
