from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Etudiant
from .serializers import EtudianteSerializer
from .utils import generate_modern_qr
from io import BytesIO

class EtudianteViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.all()
    serializer_class = EtudianteSerializer

    @action(detail=True, methods=['get'])
    def download_qr(self, request, pk=None):
        student = self.get_object()
        
        # Génération de l'image
        badge = generate_modern_qr(student)
        
        # Préparation de la réponse HTTP pour téléchargement
        buffer = BytesIO()
        badge.save(buffer, format="PNG")
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type="image/png")
        response['Content-Disposition'] = f'attachment; filename="QR_{student.matricule}.png"'
        return response