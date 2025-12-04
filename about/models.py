from django.db import models
#from django.conf import settings

class About(models.Model):
    titre = models.CharField(max_length=50, blank=True, null=True)
    contenu = models.TextField()
