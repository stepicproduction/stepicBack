from rest_framework import serializers
from utilisateur.serializers import UtilisateurSerializer
from .models import Showreel

class ShowreelSerializer(serializers.ModelSerializer):
    user = UtilisateurSerializer(read_only=True)
    class Meta:
        model = Showreel
        fields = "__all__"