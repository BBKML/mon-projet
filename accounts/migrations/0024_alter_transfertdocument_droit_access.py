# Generated by Django 4.2 on 2024-12-19 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('accounts', '0023_alter_transfertdocument_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transfertdocument',
            name='droit_access',
            field=models.ManyToManyField(to='auth.permission', verbose_name="Droit d'accès"),
        ),
    ]
