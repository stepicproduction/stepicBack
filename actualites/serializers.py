from rest_framework import serializers
from utilisateur.serializers import UtilisateurSerializer
from .models import Blog

class BlogSerializer(serializers.ModelSerializer):
    user = UtilisateurSerializer(read_only=True)
    datePub = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%s", read_only=True)

    class Meta:
        model = Blog
        fields = "__all__"