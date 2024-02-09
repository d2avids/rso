from django.contrib.auth.hashers import make_password
from import_export import resources
from users.models import RSOUser


class RSOUserResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        if 'password' in row and row['password']:
            row['password'] = make_password(row['password'])

    class Meta:
        model = RSOUser
        fields = ('username', 'first_name', 'last_name', 'password')
        export_order = ('username', 'first_name', 'last_name', 'password')
        import_id_fields = ()
