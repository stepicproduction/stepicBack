from django.db import models
from django.conf import settings

class Blog(models.Model):
    titreActu = models.CharField(max_length=50)
    contenuActu = models.TextField()
    imageActu = models.ImageField(upload_to="actualites/", null=True, blank=True)
    datePub = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="Actualite_crees")

