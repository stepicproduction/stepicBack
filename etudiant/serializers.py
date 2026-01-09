from rest_framework import serializers
from .models import Etudiant
from service.models import Service

class EtudiantSerializer(serializers.ModelSerializer):
    # 1. Pour l'affichage (GET) : on récupère le nom du service et de la catégorie
    parcours_nom = serializers.ReadOnlyField(source='parcours.nom')
    categorie_nom = serializers.ReadOnlyField(source='parcours.categorie.nom')
    
    # 2. Lien vers le QR Code (Optionnel : pour que le front sache où le télécharger)
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Etudiant
        # 'parcours' attend l'ID du service lors d'un POST/PUT (venant de ton select front)
        fields = [
            'id', 
            'nom', 
            'prenom', 
            'matricule', 
            'parcours', 
            'parcours_nom', 
            'categorie_nom',
            'qr_code_url'
        ]

    def get_qr_code_url(self, obj):
        # Génère dynamiquement l'URL vers l'action download_qr du ViewSet
        request = self.context.get('request')
        if request is not None:
            # Retourne l'URL complète : https://.../api/etudiants/1/download_qr/
            return request.build_absolute_uri(f'/api/etudiants/{obj.id}/download_qr/')
        return None