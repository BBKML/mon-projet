from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import Role, Document, Folder
from .models import TransfertDocument


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['folder'].queryset = Folder.objects.filter(uploaded_by=user)
class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']

class DocumentUpdateForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['folder'].queryset = Folder.objects.filter(created_by=user)

class DecryptionCodeForm(forms.Form):
    code = forms.CharField(
        max_length=8,
        label="Code de déchiffrement",
        widget=forms.TextInput(attrs={'placeholder': 'Entrez le code', 'class': 'form-control'})
    )

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'permissions']
class TransfertDocumentForm(forms.ModelForm):
    class Meta:
        model = TransfertDocument
        fields = '__all__' 

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Limite le choix du destinataire au seul utilisateur qui peut recevoir le document
            self.fields['recipient'].queryset = User.objects.exclude(id=user.id)