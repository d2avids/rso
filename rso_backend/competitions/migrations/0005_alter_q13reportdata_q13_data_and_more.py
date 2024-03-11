# Generated by Django 4.2.7 on 2024-03-10 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0004_q13detachmentreport_q13eventorganization_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='q13reportdata',
            name='q13_data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_data', to='competitions.q13eventorganization'),
        ),
        migrations.AlterField(
            model_name='q13reportdata',
            name='q13_report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_data', to='competitions.q13detachmentreport'),
        ),
    ]