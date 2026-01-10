from rest_framework import serializers
from .models import Etudiant
from inscription.serializers import InscriptionSerializer

class EtudiantSerializer(serializers.ModelSerializer):
    # On imbrique le serializer de l'inscription pour avoir tous les détails (nom, services, etc.)
    inscription_details = InscriptionSerializer(source='inscription', read_only=True)
    
    # On peut aussi extraire juste des champs spécifiques si besoin
    nom_complet = serializers.SerializerMethodField()

    class Meta:
        model = Etudiant
        fields = ['id', 'matricule', 'date_creation', 'inscription', 'inscription_details', 'nom_complet']

    def get_nom_complet(self, obj):
        return f"{obj.inscription.nomClient} {obj.inscription.prenomClient}"

    def get_qr_code_url(self, obj):
        # Génère dynamiquement l'URL vers l'action download_qr du ViewSet
        request = self.context.get('request')
        if request is not None:
            # Retourne l'URL complète : https://.../api/etudiants/1/download_qr/
            return request.build_absolute_uri(f'/api/etudiants/{obj.id}/download_qr/')
        return None