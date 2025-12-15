from rest_framework import serializers
from .models import Inscription
from utilisateur.serializers import UtilisateurSerializer
from service.serializers import ServiceSerializer
from service.serializers import CategorieSerializer
from service.models import Service
from service.models import Categorie

class InscriptionSerializer(serializers.ModelSerializer):
    client = UtilisateurSerializer(read_only=True)

    dateInscription = serializers.DateTimeField(format="%Y-%m-%d", required=False)

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True)
    
    categorie = serializers.PrimaryKeyRelatedField(queryset=Categorie.objects.all())
    
    service_detail = ServiceSerializer(source="service", many=True, read_only=True)

    categorie_detail = CategorieSerializer(source="categorie", read_only=True)

    statut = serializers.SerializerMethodField()
    
    class Meta:
        model = Inscription
        fields = "__all__"

    def get_statut(self, obj):
        return "Validé" if obj.statut else "En attente"