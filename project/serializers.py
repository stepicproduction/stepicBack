from rest_framework import serializers
from .models import Projet
from utilisateur.serializers import UtilisateurSerializer
from service.serializers import ServiceSerializer
from service.models import Service

class ProjetSerializer(serializers.ModelSerializer):
    user = UtilisateurSerializer(read_only=True)
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        required=False,
        allow_null=True
    )
    service_detail = ServiceSerializer(source="service", read_only=True)
    
    class Meta:
        model = Projet
        fields = "__all__"