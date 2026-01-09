from django.db import models
from service.models import Service

class Etudiant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    matricule = models.CharField(max_length=50, unique=True)
    parcours = models.ForeignKey(Service, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.matricule} - {self.nom}"