from django.db import models
from django.conf import settings
from django.utils import timezone


class Presse(models.Model):
    titre = models.CharField(max_length=200)
    source = models.CharField(max_length=200, null=True, blank=True)
    contenu = models.TextField()
    image = models.ImageField(upload_to="presse/", blank=True, null=True)
    date_pub = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="Presse_crees")

    def __str__(self):
        return self.titre
