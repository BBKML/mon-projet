from django.contrib import admin
from django.db.models.signals import post_migrate
from django.apps import AppConfig
from django.contrib.auth.models import Group, User
from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import Role, Folder, Service, TypeDocument, Document, TransfertDocument,Permission
from .forms import DocumentForm  # Importez le formulaire personnalisé

# Création de groupes d'utilisateurs par défaut
def create_groups(sender, **kwargs):
    default_groups = ['Utilisateurs UNA', 'Superutilisateurs UNA']
    for group_name in default_groups:
        Group.objects.get_or_create(name=group_name)

# Configuration de l'application pour connecter le signal post_migrate
class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        post_migrate.connect(create_groups, sender=self)

# Administration des rôles
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)
    list_display = ('name', 'permissions_list')

    def permissions_list(self, obj):
        return ", ".join(permission.name for permission in obj.permissions.all())
    permissions_list.short_description = _('Permissions')

# Administration des dossiers
@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('folder_icon', 'name', 'parent', 'view_documents_link', 'document_count', 'created_at', 'uploaded_by')
    search_fields = ('name', 'parent__name', 'uploaded_by__username')
    date_hierarchy = 'created_at'
    list_per_page = 5

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Superutilisateurs UNA').exists():
            return qs
        return qs.filter(uploaded_by=request.user)

    def document_count(self, obj):
        """Affiche le nombre de documents dans le dossier."""
        return obj.documents.count()
    document_count.short_description = _("Nombre de documents")

    def view_documents_link(self, obj):
        """Génère un lien vers une page admin filtrant les documents du dossier."""
        url = reverse('admin:accounts_document_changelist') + f"?folder__id__exact={obj.id}"
        return format_html(
            '<a href="{}" style="color: white; background: blue; padding: 2px 0px; text-decoration: none; border-radius: 2px;">{}</a>',
            url, _("Voirdocuments")
        )
    view_documents_link.short_description = _("Actions")

# Administration des services
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    search_fields = ('name',)
    list_per_page = 4

# Administration des types de documents
@admin.register(TypeDocument)
class TypeDocumentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 5

# Administration des documents
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentForm  # Use the custom form
    list_display = ('file_icon', 'title', 'type', 'service', 'category', 'archived','action_buttons','uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at', 'type', 'service', 'category', 'archived')
    search_fields = ('title', 'uploaded_by__username', 'type__name', 'service__name', 'category')
    date_hierarchy = 'uploaded_at'
    actions = ['mark_as_archived']
    list_per_page = 4

 
    @admin.display(description="Actions")
    def action_buttons(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            return format_html(
                '''
                <a href="{url}" target="_blank" class="button" style="background: green; color: white; padding: 2px; border-radius: 3px; text-decoration: none;">Lire</a>
                <a href="{url}" download class="button" style="background: blue; color: white; padding: 2px; border-radius: 3px; text-decoration: none; margin-left: 3px;">Télécharger</a>
                ''',
                url=obj.file.url
            )
        return ""

   
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Superutilisateurs UNA').exists():
            return qs
        return qs.filter(uploaded_by=request.user)

    def mark_as_archived(self, request, queryset):
        """Action pour archiver les documents sélectionnés."""
        count = queryset.update(archived=True)
        self.message_user(request, _("%d documents ont été archivés.") % count)
    mark_as_archived.short_description = _("Archiver les documents sélectionnés")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "folder":
            kwargs["queryset"] = Folder.objects.filter(uploaded_by=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Définit uploaded_by à l'utilisateur connecté"""
        obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
        
# Administration des transferts de documents
class TransfertDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender', 'recipient', 'status', 'document_files', 'uploaded_at')
    list_filter = ('status', 'uploaded_at', 'sender', 'recipient')
    search_fields = ('title', 'recipient__username', 'sender__username')
    filter_horizontal = ('droit_access', 'files')
    list_per_page = 5

    @admin.display(description="Document Files")
    def document_files(self, obj):
        # Vérifier si le document est lié et s'il a un fichier
        if obj.files.exists():
            return format_html(
                ''.join(
                    f'''
                    <a href="{file.file.url}" target="_blank" class="button" style="background: green; color: white; padding: 3px; border-radius: 3px; text-decoration: none;">Lire</a>
                    <a href="{file.file.url}" download class="button" style="background: blue; color: white; padding: 2px; border-radius: 3px; text-decoration: none; margin-left: 3px;">Télécharger</a>
                    <br>
                    '''
                    for file in obj.files.all()
                )
            )
        return "No files available"

    def get_request_user(self):
        """Retourne l'utilisateur courant pour l'admin"""
        from django.http import HttpRequest
        # On récupère l'utilisateur via request dans admin
        if hasattr(self, 'request'):
            return self.request.user
        return None  # Si aucune request n'est trouvée, retourne None

    def has_change_permission(self, request, obj=None):
        """Empêche la modification des transferts si l'utilisateur n'a pas la permission d'édition"""
        if obj and obj.can_edit(request.user):
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        """Empêche la suppression des transferts"""
        return True

    def has_add_permission(self, request):
        """Autorise l'ajout de nouveaux transferts"""
        return True
    
    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "files":
    #         kwargs["queryset"] = Document.objects.filter(uploaded_by=request.user)
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "files":
            kwargs["queryset"] = Document.objects.filter(uploaded_by=request.user)
        elif db_field.name == "droit_access":
            # Filtrer les permissions liées aux documents
            document_permissions = Permission.objects.filter(
                content_type__app_label='accounts',
                content_type__model='document'
            )
            kwargs["queryset"] = document_permissions
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Définit le sender par défaut à l'utilisateur connecté"""
        if not change:
            obj.sender = request.user
        super().save_model(request, obj, form, change)
        
admin.site.register(TransfertDocument, TransfertDocumentAdmin)    