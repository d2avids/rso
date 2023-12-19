from import_export import resources
from headquarters.models import Region, EducationalInstitution
from users.models import RSOUser
from django.contrib.auth.hashers import make_password


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
