from django.db import models
from django.conf import settings

class Message(models.Model):
    nomClient = models.CharField(max_length=50)
    emailClient = models.EmailField()
    sujet = models.CharField(max_length=50)
    contenu = models.TextField()
    dateMess = models.DateTimeField(auto_now_add=True)
    statut = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="message_cree") 
