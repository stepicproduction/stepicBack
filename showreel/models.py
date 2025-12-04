from django.db import models
from django.conf import settings

class Showreel(models.Model):
    # Changement: Nommage Python/Anglais pour les champs
    # Les champs peuvent rester null/blank si vous le souhaitez
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # Le lien est généralement obligatoire
    link = models.URLField(max_length=500)

    # user est correct, mais related_name devrait suivre les conventions
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="showreels" # Renommage conventionnel (anglais et pluriel)
    )

    # Suggestion: ajouter une méthode __str__ pour une meilleure représentation
    def __str__(self):
        return self.title or f"Showreel #{self.pk}"