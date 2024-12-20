from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test,permission_required
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
 
from django.http import HttpResponseForbidden

from .models import TransfertDocument
from .forms import TransfertDocumentForm
from .models import Document, Folder, TransfertDocument, Service, TypeDocument

# Vérification des rôles
def is_ged_user(user):
    """Vérifie si l'utilisateur appartient au groupe 'Utilisateurs UNA'."""
    return user.groups.filter(name='Utilisateurs UNA').exists()

def is_superuser(user):
    """Vérifie si l'utilisateur appartient au groupe 'Superutilisateurs UNA'."""
    return user.groups.filter(name='Superutilisateurs UNA').exists()

# Vue de connexion personnalisée
def custom_login(request):
    """Gère la connexion des utilisateurs."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Tableau de bord utilisateur standard
@login_required
@user_passes_test(is_ged_user)
def user_dashboard(request):
    """Affiche le tableau de bord des utilisateurs standard."""
    documents = Document.objects.filter(uploaded_by=request.user)
    context = {'documents': documents}
    return render(request, 'accounts/user_dashboard.html', context)

# Tableau de bord superutilisateur
@login_required
@user_passes_test(is_superuser)
def superuser_dashboard(request):
    """Affiche le tableau de bord des superutilisateurs."""
    documents = Document.objects.all()
    context = {'documents': documents}
    return render(request, 'accounts/superuser_dashboard.html', context)


# Recherche de documents
@login_required
def rechercherDoc(request):
    """Permet de rechercher des documents avec des filtres."""
    filters = {}
    date_str = request.GET.get('date')
    document_type = request.GET.get('documentType')
    service = request.GET.get('service')
    category = request.GET.get('category')

    if date_str:
        filters['uploaded_at__date'] = parse_date(date_str)
    if document_type:
        filters['document_type__id'] = document_type
    if service:
        filters['service__id'] = service
    if category:
        filters['category__icontains'] = category
    if not is_superuser(request.user):
        filters['uploaded_by'] = request.user

    results = Document.objects.filter(**filters)
    return render(request, 'accounts/rechercherDoc.html', {'results': results})

# Archiver un document
@login_required
def archive_document(request, pk):
    """Marque un document comme archivé."""
    document = get_object_or_404(Document, pk=pk, uploaded_by=request.user)
    document.archived = True
    document.save()
    messages.success(request, 'Document archivé avec succès.')
    return redirect('archived_documents')

# Restaurer un document
@login_required
def restore_document(request, pk):
    """Restaure un document archivé."""
    document = get_object_or_404(Document, pk=pk, uploaded_by=request.user)
    document.archived = False
    document.save()
    messages.success(request, 'Document restauré avec succès.')
    return redirect('archived_documents')

# Gestion des documents archivés
@login_required
def archived_documents(request):
    """Affiche la liste des documents archivés."""
    if is_superuser(request.user):
        documents = Document.objects.filter(archived=True)
    else:
        documents = Document.objects.filter(archived=True, uploaded_by=request.user)
    return render(request, 'accounts/archived_documents.html', {'documents': documents})

# Page d'accueil
def home(request):
    """Affiche la page d'accueil."""
    return render(request, 'accounts/main.html')

# Génération d'un rapport des documents (API REST)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rapport(request):
    """Génère un rapport des documents au format JSON."""
    if is_superuser(request.user):
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(uploaded_by=request.user)

    report_data = [
        {
            'title': document.title,
            'uploaded_by': document.uploaded_by.username,
            'uploaded_at': document.uploaded_at,
            'document_type': document.document_type.name if document.document_type else 'N/A',
            'service': document.service.name if document.service else 'N/A',
            'category': document.category,
            'archived': document.archived,
        }
        for document in documents
    ]
    return Response(report_data)



@login_required
@permission_required('accounts.view_transfertdocument', raise_exception=True)
def access_document(request, transfert_id):
    """Permet d'accéder à un document via un transfert."""
    transfert = get_object_or_404(TransfertDocument, id=transfert_id)
    if request.user != transfert.recipient:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à accéder à ce document.")
    return render(request, 'accounts/access_document.html', {'transfert': transfert})

@login_required
def access_document(request, transfert_id):
    """Permet d'accéder à un document via un transfert."""
    transfert = get_object_or_404(TransfertDocument, id=transfert_id)
    if request.user != transfert.recipient:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à accéder à ce document.")
    return render(request, 'accounts/access_document.html', {'transfert': transfert})