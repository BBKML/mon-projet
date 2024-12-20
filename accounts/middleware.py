from django.http import HttpResponseForbidden
from django.conf import settings
import os

class ProtectedMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(settings.MEDIA_URL):
            # Ajoutez votre logique pour vérifier si l'utilisateur a le droit d'accéder au fichier
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Non autorisé.")
        return self.get_response(request)
