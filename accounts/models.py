from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import User


class Role(models.Model):
    name = models.CharField(max_length=255)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')

    def __str__(self):
        return self.name

class User(AbstractUser):
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set', blank=True)



class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.name
    

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_type = models.CharField(max_length=100, blank=True)
    service = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    archived = models.BooleanField(default=False) 
    class Meta:
        permissions = [
            ("can_view_document", "Can view document"),
            ("can_edit_document", "Can edit document"),
            ("can_archivate_document", "can archivate_document"),
            ("can_generate_rapport", "can_generate_rapport"),
            ("can-view-user-dashboard", "can-view-user-dashboard"),
            ("can-view-page-suivi", "can-view-page-suivi"),
            ("can-enregistrate-doc", "can-enregistrate-doc"),
            ("can_searchDoc", "can_searchDoc"),
            ("can-view-superuser-dashboard", "can-view-superuser-dashboard"),
            ("can-view-page-suivi2", "can-view-page-suivi2"),
            ("can_create-folder", "can_create-folder"),
            ("can_deletedoc", "can_deletedoc")

        ]

    def __str__(self):  # Utilisez __str__ au lieu de _str_
        return self.title
    
