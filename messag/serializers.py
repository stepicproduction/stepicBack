from rest_framework import serializers
from .models import Message
from utilisateur.serializers import UtilisateurSerializer

class MessageSerializer(serializers.ModelSerializer):
    user = UtilisateurSerializer(read_only=True)

    dateMess = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    statut = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = "__all__"

    def get_statut(self, obj):
        return "Lu" if obj.statut else "Non lu"