from rest_framework import serializers
from utilisateur.serializers import UtilisateurSerializer
from .models import Presse

class PresseSerializers(serializers.ModelSerializer):
    user = UtilisateurSerializer(read_only=True)
    date_pub = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)
    class Meta:
        model = Presse
        fields = "__all__"