from import_export import resources
from headquarters.models import Region


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
