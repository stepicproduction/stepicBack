from django.db import models
from django.conf import settings

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    image = models.ImageField(upload_to="categorie/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    button = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nom

class Service(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name="offres", blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="service/", null=True, blank=True)
    button = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="services_crees")
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
