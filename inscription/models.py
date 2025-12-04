from django.db import models
from django.conf import settings
from service.models import Service, Categorie

class Inscription(models.Model):
    nomClient = models.CharField(max_length=50)
    prenomClient = models.CharField(max_length=50)
    emailClient = models.EmailField()
    telephoneClient = models.CharField(max_length=20, null=True, blank=True)
    dateInscription = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
    blank=True, related_name="inscription_crees")
    statut = models.BooleanField(default=False)
    service = models.ManyToManyField(Service, related_name="inscriptions")
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name="inscription_categorie", blank=True, null=True)