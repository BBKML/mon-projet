# Generated by Django 5.0.7 on 2024-07-23 14:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_document_archived'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={'permissions': [('can_view_document', 'Can view document'), ('can_edit_document', 'Can edit document'), ('can_archivate_document', 'can archivate_document'), ('can_generate_rapport', 'can_generate_rapport'), ('can-view-user-dashboard', 'can-view-user-dashboard'), ('can-view-page-suivi', 'can-view-page-suivi'), ('can-enregistrate-doc', 'can-enregistrate-doc'), ('can_searchDoc', 'can_searchDoc'), ('can-view-superuser-dashboard', 'can-view-superuser-dashboard'), ('can-view-page-suivi2', 'can-view-page-suivi2'), ('can_create-folder', 'can_create-folder'), ('can_deletedoc', 'can_deletedoc')]},
        ),
    ]
