from django.shortcuts import render
from rest_framework import viewsets
from .models import Projet
from .serializers import ProjetSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class ProjetViewSet(viewsets.ModelViewSet):
    queryset = Projet.objects.all()
    serializer_class = ProjetSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print("🔹 Données reçues:", request.data)      # Affiche les données du POST
        print("🔹 Fichiers reçus:", request.FILES)     # Affiche les fichiers uploadés
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("❌ Erreurs de validation:", serializer.errors)  # Affiche les erreurs du serializer
            return Response(serializer.errors, status=400)         # Renvoie les erreurs en JSON
        

        self.perform_create(serializer)
        return Response(serializer.data, status=201)


