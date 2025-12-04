from django.core.mail import send_mail
from django.conf import settings
from .models import Commande

def send_email(commande_id):
    try:
        commande = Commande.objects.get(id=commande_id)
    except Commande.DoesNotExist:
        print(f"Erreur : Commande ID {commande_id} non trouvée")
        return
    
    services_list = ", ".join([s.nom_service for s in commande.services_choisis.all()]) or "Aucun"