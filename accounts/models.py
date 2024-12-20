from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
import os

# Modèle pour les rôles personnalisés
class Role(models.Model):
    name = models.CharField(max_length=255)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='roles')

    def __str__(self):
        return self.name

# Modèle utilisateur personnalisé
class CustomUser(AbstractUser):
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set', blank=True)

# Modèle pour les dossiers
class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def folder_icon(self):
        return format_html('<i class="fas fa-folder" style="color: #ffa726;"></i>')

    folder_icon.short_description = "Dossier"
    
    def save(self, *args, **kwargs):
        if not self.uploaded_by:
            self.uploaded_by = kwargs.pop('user', None)
        super().save(*args, **kwargs)
# Modèle pour les services
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.name

# Modèle pour les types de documents
class TypeDocument(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Modèle pour les documents
class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    type = models.ForeignKey(TypeDocument, on_delete=models.CASCADE,null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE,null=True, blank=True)
    category = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE,related_name="documents",null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("can_view_document", "Can view document"),
            ("can_edit_document", "Can edit document"),
            ("can_archivate_document", "Can archive document"),
            ("can_generate_rapport", "Can generate rapport"),
            ("can_view_user_dashboard", "Can view user dashboard"),
            ("can_view_page_suivi", "Can view page suivi"),
            ("can_enregistrate_doc", "Can enregistrate document"),
            ("can_search_doc", "Can search document"),
            ("can_view_superuser_dashboard", "Can view superuser dashboard"),
            ("can_create_folder", "Can create folder"),
            ("can_delete_doc", "Can delete document"),
        ]

    def __str__(self):
        return self.title

    def file_icon(self):
        extension = os.path.splitext(self.file.name)[1].lower()
        icons = {
            '.jpg': 'fas fa-file-image',
            '.jpeg': 'fas fa-file-image',
            '.png': 'fas fa-file-image',
            '.gif': 'fas fa-file-image',
            '.pdf': 'fas fa-file-pdf',
            '.doc': 'fas fa-file-word',
            '.docx': 'fas fa-file-word',
            '.xls': 'fas fa-file-excel',
            '.xlsx': 'fas fa-file-excel',
        }
        icon = icons.get(extension, 'fas fa-file')
        color = {
            'fas fa-file-image': '#4caf50',
            'fas fa-file-pdf': '#f44336',
            'fas fa-file-word': '#2196f3',
            'fas fa-file-excel': '#4caf50',
        }.get(icon, '#9e9e9e')
        return format_html(f'<i class="{icon}" style="color: {color};"></i>')

    file_icon.short_description = "File Icon"

    def document_files(self):
            return format_html(
                ''.join(
                    f'''
                    <a href="{file.file.url}" target="_blank" class="button" style="background: green; color: white; padding: 3px; border-radius: 3px; text-decoration: none;">Lire</a>
                    <a href="{file.file.url}" download class="button" style="background: blue; color: white; padding: 2px; border-radius: 3px; text-decoration: none; margin-left: 3px;">Télécharger</a>
                    <br>
                    '''
                    for file in self.files.all()
                )
            )

    document_files.short_description = "Actions"
    
    def save(self, *args, **kwargs):
        if not self.uploaded_by:
            self.uploaded_by = kwargs.pop('user', None)
        super().save(*args, **kwargs)

# Modèle pour le transfert de documents
# Modèle pour le transfert de documents
class TransfertDocument(models.Model):
    title = models.CharField(max_length=255)
    sender = models.ForeignKey(
        User, related_name='sent_transfers', on_delete=models.CASCADE, null=True, blank=True
    )
    recipient = models.ForeignKey(
        User, related_name='received_transfers', on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=[('pending', _('En attente')), ('approved', _('Approuvé')), ('rejected', _('Rejeté'))],
        default='pending',
        verbose_name=_("Statut")
    )
    files = models.ManyToManyField(
        Document, related_name="transfers", verbose_name=_("Documents")
    )
    droit_access = models.ManyToManyField(Permission, verbose_name=_("Droit d'accès"))
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_view_document", _("Can view document")),
            ("can_edit_document", _("Can edit document")),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def can_edit(self, user):
        """Vérifie si un utilisateur a les permissions pour éditer ce transfert"""
        if user.has_perm('accounts.can_edit_document') or user == self.sender:
            return True
        return False

    def can_view(self, user):
        """Vérifie si un utilisateur a les permissions pour voir ce transfert"""
        if user.has_perm('accounts.can_view_document') or user == self.recipient:
            return True
        return False

    def document_files(self):
        return format_html(
            ''.join(
                f'''
                <a href="{file.url}" target="_blank" class="button" style="background: green; color: white; padding: 3px; border-radius: 3px; text-decoration: none;">Lire</a>
                <a href="{file.url}" download class="button" style="background: blue; color: white; padding: 2px; border-radius: 3px; text-decoration: none; margin-left: 3px;">Télécharger</a>
                <br>
                '''
                for file in self.files.all()
            )
        )

    document_files.short_description = "Actions"

@receiver(m2m_changed, sender=TransfertDocument.files.through)
def validate_files(sender, instance, action, **kwargs):
    if action == 'post_add' and not instance.files.exists():
        raise ValidationError(_("Le champ 'files' est obligatoire."))