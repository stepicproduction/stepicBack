from django.shortcuts import render
from rest_framework import viewsets
from .models import About
from .serializers import AboutSerializer
from rest_framework.permissions import AllowAny

class AboutViewSet(viewsets.ModelViewSet):
    queryset = About.objects.all()
    serializer_class = AboutSerializer
    permission_classes = [AllowAny]
