from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny # Ou IsAuthenticated selon tes besoins
from django.http import HttpResponse
from io import BytesIO

from .models import Etudiant
from .serializers import EtudiantSerializer
from .utils import generate_modern_qr  # Ta fonction de génération

class EtudiantViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.all()
    serializer_class = EtudiantSerializer
    permission_classes = [AllowAny] # À sécuriser plus tard avec IsAuthenticated

    def perform_create(self, serializer):
        """
        Logique personnalisée lors de la création si nécessaire.
        Ici, on sauvegarde simplement l'étudiante.
        """
        serializer.save()


    def get_queryset(self):
        queryset = Etudiant.objects.all()
        matricule = self.request.query_params.get('matricule')
        if matricule is not None:
            queryset = queryset.filter(matricule=matricule)
        return queryset

    @action(detail=True, methods=['get'], url_path='download_qr')
    def download_qr(self, request, pk=None):
        """
        Endpoint : GET /api/etudiants/{id}/download_qr/
        Génère et renvoie le badge QR Code en format PNG.
        """
        try:
            # 1. Récupérer l'étudiante (inclut automatiquement les infos du parcours lié)
            student = self.get_object()
            
            # 2. Générer l'image du badge (en utilisant ta fonction Pillow)
            badge = generate_modern_qr(student)
            
            # 3. Préparer le fichier en mémoire (RAM) pour l'envoi
            buffer = BytesIO()
            badge.save(buffer, format="PNG")
            buffer.seek(0)
            
            # 4. Retourner le fichier en tant que réponse HTTP
            response = HttpResponse(buffer, content_type="image/png")
            response['Content-Disposition'] = f'attachment; filename="Badge_{student.matricule}.png"'
            return response
            
        except Etudiante.DoesNotExist:
            return Response({"error": "Étudiante non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='count')
    def count_etudiants(self, request):
        """
        Endpoint : GET /api/etudiants/count/
        Utile pour ton tableau de bord front-end.
        """
        total = Etudiante.objects.count()
        return Response({'total': total})