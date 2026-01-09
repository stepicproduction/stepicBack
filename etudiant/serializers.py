from rest_framework import serializers
from .models import Etudiant

class EtudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etudiant
        fields = '__all__'