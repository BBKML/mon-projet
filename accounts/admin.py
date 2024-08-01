from django.contrib import admin
from .models import Contact
from .models import Document,Folder
admin.site.register(Contact)
from django.contrib.auth.models import Group, User
from .models import Role
# Création de groupes d'utilisateurs
def create_groups(sender, **kwargs):
    if not Group.objects.filter(name='Utilisateurs GED').exists():
        Group.objects.create(name='Utilisateurs GED')
    if not Group.objects.filter(name='Superutilisateurs GED').exists():
        Group.objects.create(name='Superutilisateurs GED')

# Connecter la création de groupes au signal de migration de Django
from django.db.models.signals import post_migrate
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'accounts'
    
    def ready(self):
        post_migrate.connect(create_groups, sender=self)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'document_type', 'service', 'category','archived')
    list_filter = ('uploaded_at', 'document_type', 'service', 'category','archived')
    search_fields = ('title', 'uploaded_by', 'document_type', 'service', 'category','archived')
    date_hierarchy = 'uploaded_at'

admin.site.register(Document, DocumentAdmin)
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    
    filter_horizontal = ('permissions',)
    list_display = ('name', 'permissions_list')  # Assurez-vous que c'est une liste ou un tuple

    def permissions_list(self, obj):
        return ", ".join(permission.name for permission in obj.permissions.all())
    permissions_list.short_description = 'Permissions'


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')  # Affiche les informations principales de l'utilisateur
    search_fields = ('username', 'email', 'first_name', 'last_name')  # Permet de rechercher par ces champs

admin.site.register(Folder)