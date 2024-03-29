# Generated by Django 4.0.5 on 2024-02-04 23:00

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'verbose_name': 'file', 'verbose_name_plural': 'files'},
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together={('name', 'user')},
        ),
    ]
