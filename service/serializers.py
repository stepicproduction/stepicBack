from rest_framework import serializers
from .models import Service, Categorie
from utilisateur.serializers import UtilisateurSerializer

class CategorieSerializer(serializers.ModelSerializer):
    # On peut inclure les services associés, en lecture seule pour éviter boucle infinie
    service = serializers.StringRelatedField(many=True, read_only=True)  

    class Meta:
        model = Categorie
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    user = UtilisateurSerializer(read_only=True)
    
    # On garde juste la PK pour l'écriture
    categorie = serializers.PrimaryKeyRelatedField(queryset=Categorie.objects.all())
    
    # Détail en lecture seule pour l'affichage
    categorie_detail = CategorieSerializer(source="categorie", read_only=True)
    
    class Meta:
        model = Service
        fields = "__all__"
