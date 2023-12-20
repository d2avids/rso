import datetime

from import_export import resources
from headquarters.models import Region, EducationalInstitution, DistrictHeadquarter


class DistrictHeadquarterResource(resources.ModelResource):
    def skip_row(self, instance, original, row, import_validation_errors=None):
        """
        Пропускает строки без "name" и "central_headquarter".
        """
        if 'name' not in row or not row['name']:
            return True
        if 'central_headquarter' not in row or not row['central_headquarter']:
            return True

    class Meta:
        model = DistrictHeadquarter
        fields = ('name', 'central_headquarter')
        export_order = ('name', 'central_headquarter')
        import_id_fields = ()


class RegionResource(resources.ModelResource):

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """
        Пропускает строки без "name".
        """
        if 'name' not in row or not row['name']:
            return True

        return super().skip_row(instance, original, row, import_validation_errors)

    class Meta:
        model = Region


class RegionResource(resources.ModelResource):

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """
        Пропускает строки без "name".
        """
        if 'name' not in row or not row['name']:
            return True

        return super().skip_row(instance, original, row, import_validation_errors)

    class Meta:
        model = Region


class EducationalInstitutionResource(resources.ModelResource):
    def skip_row(self, instance, original, row, import_validation_errors=None):
        """
        Пропускает строки без "region".
        """
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
