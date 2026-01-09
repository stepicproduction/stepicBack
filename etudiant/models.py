from django.db import models

class Etudiant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    matricule = models.CharField(max_length=50, unique=True)
    parcours = models.CharField(max_length=150)
    # On garde le champ au cas où vous voudriez aussi l'afficher sur le profil
    qr_code_url = models.URLField(blank=True, null=True) 

    def __str__(self):
        return f"{self.matricule} - {self.nom}"