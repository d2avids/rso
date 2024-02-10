import datetime

from import_export import fields, resources

from headquarters.models import (DistrictHeadquarter, EducationalInstitution,
                                 Region, RegionalHeadquarter)
from users.models import RSOUser


class RegionWidget(resources.widgets.ForeignKeyWidget):
    def clean(self, value, row=None, **kwargs):

        try:
            return self.model.objects.get(name=value)
        except self.model.DoesNotExist:
            return None


class RegionalHeadquarterResource(resources.ModelResource):
    region = fields.Field(
        column_name='region',
        attribute='region',
        widget=RegionWidget(Region, 'name')
    )

    def before_import_row(self, row, **kwargs):
        """Ставит для обязательных полей дефолтные значения."""
        if 'conference_date' not in row or not row['conference_date']:
            row['conference_date'] = datetime.datetime.now().date()
        if 'founding_date' not in row or not row['founding_date']:
            row['founding_date'] = 1970

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Пропускает определенные строки."""
        if 'name' not in row or not row['name']:
            return True
        if 'region' not in row or not row['region']:
            return True
        if 'address' not in row or not row['address']:
            return True
        if 'case_name' not in row or not row['case_name']:
            return True
        if 'legal_address' not in row or not row['legal_address']:
            return True
        if 'name_for_certificates' not in row or not row['name_for_certificates']:
            return True
        if 'requisites' not in row or not row['requisites']:
            return True
        if 'district_headquarter' not in row or not row['district_headquarter']:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    class Meta:
        model = RegionalHeadquarter
        fields = (
            'name',
            'requisites',
            'region',
            'district_headquarter',
            'case_name',
            'legal_address',
            'name_for_certificates',
            'commander',
            'conference_date',
            'founding_date',
        )
        export_order = (
            'name',
            'requisites',
            'region',
            'district_headquarter',
            'case_name',
            'legal_address',
            'name_for_certificates',
            'commander',
            'conference_date',
            'founding_date',
        )
        import_id_fields = (
            'region',
            'district_headquarter',
        )


class DistrictHeadquarterResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        """Ставит для обязательных полей дефолтные значения."""
        if 'founding_date' not in row or not row['founding_date']:
            row['founding_date'] = datetime.datetime.now().date()
        if 'commander' not in row or not row['commander']:
            row['commander'] = RSOUser.objects.first().id

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Пропускает строки без "name" и "central_headquarter"."""
        if 'name' not in row or not row['name']:
            return True
        if 'central_headquarter' not in row or not row['central_headquarter']:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    class Meta:
        model = DistrictHeadquarter
        fields = ('name', 'central_headquarter', 'founding_date', 'commander')
        export_order = ('name', 'central_headquarter', 'founding_date', 'commander')
        import_id_fields = ()


class RegionResource(resources.ModelResource):
    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Пропускает строки без "name"."""
        if 'name' not in row or not row['name']:
            return True

        return super().skip_row(instance, original, row, import_validation_errors)

    class Meta:
        model = Region


class EducationalInstitutionResource(resources.ModelResource):
    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Пропускает строки без "region"."""
        if 'region' not in row or not row['region']:
            return True
        elif 'short_name' not in row or not row['short_name']:
            return True

        return super().skip_row(instance, original, row, import_validation_errors)

    class Meta:
        model = EducationalInstitution
        skip_unchanged = True
        report_skipped = False
        verbose_name = True
