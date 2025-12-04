from django.db import models
from django.conf import settings

class Temoignage(models.Model):
    nomClient = models.CharField(max_length=100)
    prenomClient = models.CharField(max_length=200, blank=True, null=True)
    messageClient = models.TextField()
    role = models.CharField(max_length=100, blank=True, null=True)
    dateTem = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="temoin/", null=True, blank=True)
    note = models.PositiveIntegerField(default=5)
    email = models.EmailField(unique=True, blank=True, null=True)
    valide =  models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="temoignage_cree")
