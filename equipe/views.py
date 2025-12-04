from django.shortcuts import render
from rest_framework import viewsets
from .serializers import EquipeSerializers
from .models import Equipe
from rest_framework.permissions import AllowAny


class EquipeModelViewSet(viewsets.ModelViewSet):
    queryset = Equipe.objects.all()
    serializer_class = EquipeSerializers
    permission_classes = [AllowAny]

