from django.shortcuts import render
from rest_framework import viewsets
from .models import Temoignage
from .serializers import TemoignageSearilezer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class TemoignageViewSet(viewsets.ModelViewSet):
    queryset = Temoignage.objects.all()
    serializer_class = TemoignageSearilezer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='count/en_attente')
    def attente(self, request):
        temoignage = Temoignage.objects.filter(valide=False).count()
        #serializer = self.get_serializer(temoignage, many=True)
        return Response({'temoignage_en_attente' : temoignage })
    
    @action(detail=False, methods=['get'], url_path='en_attente')
    def attenteData(self, request):
        temoignage = Temoignage.objects.filter(valide=False)
        serializer = self.get_serializer(temoignage, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='count/valide')
    def valider(self, request):
        temoignage = Temoignage.objects.filter(valide=True).count()
        #serializer = self.get_serializer(temoignage, many=True)
        #return Response(serializer.data)
        return Response({'temoignage_valide': temoignage })
    
    @action(detail=False, methods=['get'], url_path='valide')
    def valideData(self, request):
        temoignage = Temoignage.objects.filter(valide=True)
        serializer = self.get_serializer(temoignage, many=True)
        return Response(serializer.data)
        #return Response({'temoignage_valide': temoignage })
    
    @action(detail=True, methods=['put'], url_path='valider_temoin')
    def valider_temoignage(self, request, pk=None):
        try:
            temoignage = self.get_object()
            temoignage.valide = True
            temoignage.save()
            return Response({"message": "Témoignage validé avec succès."})

        except Exception as e:
            print("Erreur lors de la validation :", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
