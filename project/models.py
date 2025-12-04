from django.db import models
from django.conf import settings
from service.models import Service

class Projet(models.Model):
    titre_projet = models.CharField(max_length=100)
    description_projet = models.TextField()
    image = models.ImageField(upload_to="projet/", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="projets_crees")
