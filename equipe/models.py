from django.db import models

class Equipe(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=200)
    email = models.EmailField(unique=True, null=True, blank=True)
    image = models.ImageField(upload_to="equipe/", null=True, blank=True)
    role = models.TextField()

    def __str__(self):
        return self.nom
