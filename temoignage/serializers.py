from rest_framework import serializers
from .models import Temoignage
from utilisateur.serializers import UtilisateurSerializer

class TemoignageSearilezer(serializers.ModelSerializer):
    client = UtilisateurSerializer(read_only=True)
    dateTem = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    valide = serializers.SerializerMethodField()
    class Meta:
        model = Temoignage
        fields = "__all__"

    def get_valide(self, obj):
        return "Validé" if obj.valide else "En attente"