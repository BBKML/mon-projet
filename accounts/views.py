from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from .forms import CreateUserForm, ContactForm
from django.contrib import messages

from django.http import JsonResponse

from .models import Document
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.shortcuts import  get_object_or_404
from .models import  Folder
from .forms import DocumentForm, FolderForm,DocumentUpdateForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required



def home(request):
    return render(request, 'accounts/dashboard.html')

def is_ged_user(user):
    return user.groups.filter(name='Utilisateurs GED').exists()

def is_superuser(user):
    return user.groups.filter(name='Superutilisateurs GED').exists()


@login_required
@user_passes_test(is_ged_user)
def user_dashboard(request):

    documents = Document.objects.all()
    context = {
        'documents': documents,
    }
    return render(request, 'accounts/user_dashboard.html', context)
 
@login_required
@user_passes_test(is_superuser)
def superuser_dashboard(request):
    documents = Document.objects.all()
    context = {'documents': documents}
    return render(request, 'accounts/superuser_dashboard.html', context)

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.groups.filter(name='Superutilisateurs GED').exists():
                return redirect('superuser_dashboard')
            elif user.groups.filter(name='Utilisateurs GED').exists():
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Vous n\'avez pas les droits d\'accès au système GED.')
                return redirect('login')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            return redirect('login')
    return render(request, 'accounts/login.html')




def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful registration
    context = {'form': form}
    return render(request, 'accounts/register.html', context)






def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'accounts/contact.html', {'form': form})

from django.contrib.auth.decorators import login_required



@login_required
def redirection_vue(request):
    if request.user.is_superuser:
        return redirect('suivi2')  
    else:
        return redirect('suivi')



def suivi(request):
    return render(request, 'accounts/suivi.html')


#@permission_required('app.can-enregistrate-doc', raise_exception=True)
def enregistrerDoc(request):
    return render(request, 'accounts/enregistrerDoc.html')


def rapport(request):
    return render(request,"accounts/rapport.html")


def suivi2(request):
    document_count = Document.objects.filter(archived=False).count()
    return render(request, 'accounts/suivi2.html',  {
        'document_count': document_count})

from django.utils.dateparse import parse_date
@login_required          
#@permission_required('app.can_searchDoc',raise_exception=True)
def rechercherDoc(request):
    results = None
    date_str = request.GET.get('date')
    uploaded_by = request.GET.get('uploaded_by')
    document_type = request.GET.get('documentType')
    service = request.GET.get('service')
    category = request.GET.get('category')

    # Convertir la chaîne de date en objet date si elle existe
    date = parse_date(date_str) if date_str else None

    # Filtrer les documents en fonction des critères de recherche
    filters = {}

    if date:
        filters['uploaded_at__date'] = date

    if uploaded_by:
        filters['uploaded_by__icontains'] = uploaded_by

    if document_type:
        filters['document_type__iexact'] = document_type

    if service:
        filters['service__icontains'] = service

    if category:
        filters['category__icontains'] = category

    # Exécuter la requête avec les filtres
    if filters:
        results = Document.objects.filter(**filters)

    context = {'results': results}

    # Vérifier si des résultats sont trouvés ou non
    if not results:
        context['no_results'] = True

    return render(request, 'accounts/rechercherDoc.html', context)

@login_required
#@permission_required('app.can-enregistrate-doc', raise_exception=True)

def enregistrerDoc(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')  
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        files = request.FILES.getlist('file')
        if not files:
            return JsonResponse({'error': 'No files uploaded'}, status=400)
        for file in files:
            Document.objects.create(title=title, file=file, uploaded_by=request.user)
        return JsonResponse({'success': True}, status=200)
    return render(request, 'accounts/enregistrerDoc.html')


def get_document_count(request):
    total_count = Document.objects.count()
    return JsonResponse({'count': total_count})

@login_required
def get_document_report(request):
    document_count = Document.objects.count()
    start_of_month = timezone.now().replace(day=1)
    documents_this_month = Document.objects.filter(uploaded_at__gte=start_of_month).count()
    
    # Compter les types de documents
    pdf_count = Document.objects.filter(file__iendswith='.pdf').count()
    word_count = Document.objects.filter(file__iendswith='.docx').count()
    image_count = Document.objects.filter(file__iendswith__in=['.png', '.jpg', '.jpeg']).count()
    other_count = document_count - (pdf_count + word_count + image_count)

    return JsonResponse({
        'total_count': document_count,
        'this_month_count': documents_this_month,
        'pdf_count': pdf_count,
        'word_count': word_count,
        'image_count': image_count,
        'other_count': other_count
    })


#@permission_required('app.can_view_document',raise_exception=True)
def view_documents(request):
    sort_by = request.GET.get('sort_by', 'title')  
    documents = Document.objects.all().order_by(sort_by)
    return render(request, 'accounts/view_documents.html', {'documents': documents, 'sort_by': sort_by})

from django.views.generic.edit import CreateView
from .models import Role
from .forms import RoleForm

class RoleCreateView(CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'role_form.html'
    success_url = '/roles/'  # Redirection après la création

    def form_valid(self, form):
        # Traitement personnalisé, si nécessaire
        return super().form_valid(form)
    

def get_documents(request):
    documents = Document.objects.all().values('title', 'uploaded_by', 'uploaded_at', 'document_type', 'service', 'category', 'file')
    document_list = list(documents)
    return JsonResponse(document_list, safe=False)

@login_required
#@permission_required('app.can_edit_document',raise_exception=True)
#@permission_required('app.can_create-folder',raise_exception=True)
#@permission_required('app.can_deletedoc',raise_exception=True)
def manage_documents(request):
    # Initialize forms
    folder_form = FolderForm()
    document_form = DocumentForm()
    update_form = DocumentUpdateForm()

    if request.method == 'POST':
        if 'create_folder' in request.POST:
            folder_form = FolderForm(request.POST)
            if folder_form.is_valid():
                folder_form.save()
                return redirect('manage_documents')
        elif 'upload_document' in request.POST:
            document_form = DocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                document_form.save()
                return redirect('manage_documents')
        elif 'update_document' in request.POST:
            doc_id = request.POST.get('doc_id')
            document = get_object_or_404(Document, pk=doc_id)
            update_form = DocumentUpdateForm(request.POST, instance=document)
            if update_form.is_valid():
                update_form.save()
                return redirect('manage_documents')
        elif 'delete_document' in request.POST:
            doc_id = request.POST.get('doc_id')
            document = get_object_or_404(Document, pk=doc_id)
            document.delete()
            return redirect('manage_documents')
        elif 'delete_folder' in request.POST:
            folder_id = request.POST.get('folder_id')
            folder = get_object_or_404(Folder, pk=folder_id)
            folder.delete()
            return redirect('manage_documents')

    folders = Folder.objects.all()
    documents = Document.objects.all()

    return render(request, 'accounts/manage_documents.html', {
        'folder_form': folder_form,
        'document_form': document_form,
        'update_form': update_form,
        'folders': folders,
        'documents': documents,
    })
@login_required
#@permission_required('app.can_archivate_document',raise_exception=True)
def archived_documents(request):
    if request.method == 'POST':
        if 'archive_document' in request.POST:
            doc_id = request.POST.get('doc_id')
            document = get_object_or_404(Document, pk=doc_id)
            document.archived = True
            document.save()
            return redirect('archived_documents')
        elif 'restore_document' in request.POST:
            doc_id = request.POST.get('doc_id')
            document = get_object_or_404(Document, pk=doc_id)
            document.archived = False
            document.save()
            return redirect('archived_documents')

    # Documents non archivés (à archiver)
    documents = Document.objects.filter(archived=False)
    
    # Documents archivés
    archived_documents = Document.objects.filter(archived=True)

    return render(request, 'accounts/archived_documents.html', {
        'documents': documents,
        'archived_documents': archived_documents,
    })

def get_archived_document_count(request):
    archived_count = Document.objects.filter(archived=True).count()
    return JsonResponse({'count': archived_count})

@require_POST
def restore_document(request, pk):
    document = Document.objects.get(pk=pk)
    document.archived = False  
    document.save()  
    return redirect('archived_documents') 
from django.conf import settings
import os
@login_required
def archive_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    document.archived = True
    document.save()
    # Move the document file to the archived location
    old_path = document.file.path
    archived_dir = os.path.join(settings.MEDIA_ROOT, 'archived')
    os.makedirs(archived_dir, exist_ok=True)  # Ensure the directory exists
    new_path = os.path.join(archived_dir, os.path.basename(old_path))
    os.rename(old_path, new_path)
    document.file.name = 'archived/' + os.path.basename(old_path)
    document.save()
    return redirect('archived_documents')


@login_required
def restore_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    document.archived = False
    document.save()
    # Move the document file back to the original location
    old_path = document.file.path
    documents_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
    os.makedirs(documents_dir, exist_ok=True)  # Ensure the directory exists
    new_path = os.path.join(documents_dir, os.path.basename(old_path))
    os.rename(old_path, new_path)
    document.file.name = 'documents/' + os.path.basename(old_path)
    document.save()
    return redirect('archived_documents')

@require_POST
#@permission_required('app.can_deletedoc',raise_exception=True)
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    document.delete()
    return redirect('archived_documents')

