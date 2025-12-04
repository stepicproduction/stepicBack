from django.shortcuts import render
from rest_framework import viewsets
from .models import Showreel
from .serializers import ShowreelSerializer
from rest_framework.permissions import AllowAny

class ShowreelViewSet(viewsets.ModelViewSet):
    queryset = Showreel.objects.all()
    serializer_class = ShowreelSerializer
    permission_classes = [AllowAny]
