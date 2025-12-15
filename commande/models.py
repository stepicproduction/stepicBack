from django.db import models
from django.conf import settings
from service.models import Service, Categorie
from django.utils import timezone

class Commande(models.Model):
    nomClient = models.CharField(max_length=50)
    prenomClient = models.CharField(max_length=50)
    emailClient = models.EmailField()
    telephone = models.CharField(max_length=20, null=True, blank=True)
    dateCommande = models.DateTimeField(null=True, blank=True, default=timezone.now)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="commande_crees")
    statut = models.BooleanField(default=False)
    service = models.ManyToManyField(Service, related_name="commandes")
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name="commande_categorie", blank=True, null=True)

