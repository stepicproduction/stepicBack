from django.shortcuts import render
from rest_framework import viewsets
from .serializers import PresseSerializers
from .models import Presse
from rest_framework.permissions import AllowAny


class PresseViewSet(viewsets.ModelViewSet):
    queryset = Presse.objects.all()
    serializer_class = PresseSerializers
    permission_classes = [AllowAny]

