from django.db import models
from django.conf import settings

class Presse(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to="presse/", blank=True, null=True)
    date_pub = models.DateField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="Presse_crees")

    def __str__(self):
        return self.titre
