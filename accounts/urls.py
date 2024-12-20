# from django.urls import path, include
# from . import views
# from django.contrib.auth import views as auth_views
# from django.conf import settings
# from django.conf.urls.static import static
# from .views import RoleCreateView




# urlpatterns = [
    
#     path('', views.home, name='home'),
#     path('index/', views.home, name='index'),
#     path('login/', views.loginPage, name='login'),
#     path('register/', views.register, name='register'),
    
#     path('contact/', views.contact, name='contact'),
#     path('superuser-dashboard/', views.superuser_dashboard, name='superuser_dashboard'), 
#     path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
#     path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
#     path('suivi/',views.suivi,name='suivi'),
#     path('enregistrerDoc/',views.enregistrerDoc,name='enregistrerDoc'),
#     path('get_document_count/', views.get_document_count, name='get_document_count'),
#     path('voirDoc/', views.view_documents, name='view_documents'),
#     path('rechercherDoc/', views.rechercherDoc, name='rechercherDoc'),
#     path('roles/create/', RoleCreateView.as_view(), name='role_create'),
#     path('rapport/', views.rapport, name='rapport'),
#     path('get_document_report/', views.get_document_report, name='get_document_report'),
#     path('api/documents/', views.get_documents, name='get_documents'),
#     path('suivi2/',views.suivi2,name='suivi2'),
#     path('redirect/', views.redirection_vue, name='redirection_vue'),
#     path('manage/', views.manage_documents, name='manage_documents'),
#     path('archived-documents/', views.archived_documents, name='archived_documents'),
#     path('get_archived_document_count/', views.get_archived_document_count, name='get_archived_document_count'),
#     path('archive/<int:pk>/', views.archive_document, name='archive_document'),
#     path('restore/<int:pk>/', views.restore_document, name='restore_document'),
#     path('delete_document/<int:pk>/', views.delete_document, name='delete_document'),
#     #path('send-document/', send_document, name='send_document'),
#     path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
#     path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
#     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
#     path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
# ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from accounts.views import access_document
urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('superuser-dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('send-document/', views.send_document, name='send_document'),
    path('rechercher-document/', views.rechercherDoc, name='rechercher_document'),
    path('archiver-document/<int:pk>/', views.archive_document, name='archive_document'),
    path('restaurer-document/<int:pk>/', views.restore_document, name='restore_document'),
    path('documents-archives/', views.archived_documents, name='archived_documents'),
    path('document/<int:transfert_id>/', access_document, name='access_document'),
    path('send_document/', views.send_document, name='send_document'),
    # URL pour la page de connexion
    path('admin/', auth_views.LoginView.as_view(next_page='home'), name='login'),

    # URL pour la déconnexion
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
]
