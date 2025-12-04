from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employe', 'Employé'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employe')
    image = models.ImageField(upload_to="utilisateur/", null=True, blank=True)

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.username
