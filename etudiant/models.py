from django.db import models
from inscription.models import Inscription # Adapte le chemin selon ton app

class Etudiant(models.Model):
    # Lien unique : une inscription donne un seul étudiant
    inscription = models.OneToOneField(
        Inscription, 
        on_delete=models.CASCADE, 
        related_name="profil_etudiant"
    )
    # On peut extraire des données redondantes pour faciliter les recherches
    matricule = models.CharField(max_length=20, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inscription.nomClient} {self.inscription.prenomClient} ({self.matricule})"