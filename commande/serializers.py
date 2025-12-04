from rest_framework import serializers
from .models import Commande
from utilisateur.serializers import UtilisateurSerializer
from service.serializers import ServiceSerializer
from service.serializers import CategorieSerializer
from service.models import Service
from service.models import Categorie

class CommandeSerializer(serializers.ModelSerializer):
    client = UtilisateurSerializer(read_only=True)

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True)
    
    service_detail = ServiceSerializer(source="service", many=True, read_only=True)

    dateCommande = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    categorie = serializers.PrimaryKeyRelatedField(queryset=Categorie.objects.all())
    
    categorie_detail = CategorieSerializer(source="categorie", read_only=True)

    statut = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = "__all__"

    def get_statut(self, obj):
        return "Validé" if obj.statut else "En attente"