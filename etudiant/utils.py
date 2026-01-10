import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from django.conf import settings

def generate_modern_qr(student):
    inscription = student.inscription
    
    # 1. On récupère la catégorie
    categorie_nom = inscription.categorie.nom if inscription.categorie else "Formation"
    
    # 2. On récupère TOUS les services liés et on les joint par une virgule
    services_obj = inscription.service.all()
    services_noms = ", ".join([s.nom for s in services_obj]) if services_obj else "Aucun service"
    
    site_web = "www.stepic-mada.com"
    verify_url = f"https://{site_web}/verify/{student.matricule}"
    
    # 3. Contenu textuel du QR (complet)
    qr_payload = (
        f"--- STEPIC MADA ---\n"
        f"MATRICULE : {student.matricule}\n"
        f"NOM : {inscription.nomClient.upper()} {inscription.prenomClient}\n"
        f"CATÉGORIE : {categorie_nom}\n"
        f"SERVICES : {services_noms}\n" # Liste complète dans le scan
        f"VÉRIFICATION : {verify_url}\n"
    )

    # 4. Création du QR Code
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=10,
        border=2,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#2c3e50", back_color="white").convert('RGB')

    # 5. Insertion du logo (inchangé)
    try:
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'step.png')
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            qr_w, qr_h = qr_img.size
            logo_size = qr_w // 4
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)
            qr_img.paste(logo, pos)
    except Exception as e:
        print(f"Logo non chargé : {e}")

    # 6. Création du badge final
    width, qr_h_final = qr_img.size
    # On augmente un peu la hauteur du canvas (+180 au lieu de 160) pour laisser de la place aux services
    canvas_h = qr_h_final + 180 
    badge = Image.new('RGB', (width, canvas_h), 'white')
    badge.paste(qr_img, (0, 0))
    
    draw = ImageDraw.Draw(badge)
    draw.rectangle([15, qr_h_final, width-15, qr_h_final+3], fill="#3498db")

    # Texte visuel en bas du badge
    y = qr_h_final + 20
    draw.text((20, y), f"MATRICULE: {student.matricule}", fill="#e74c3c")
    draw.text((20, y + 30), f"{inscription.nomClient.upper()} {inscription.prenomClient}", fill="#2c3e50")
    
    # Affichage Catégorie + Services (tronqué si trop long pour le visuel)
    info_formation = f"{categorie_nom} ({services_noms})"
    if len(info_formation) > 40:
        info_formation = info_formation[:37] + "..."
        
    draw.text((20, y + 60), info_formation, fill="#7f8c8d")
    draw.text((20, y + 90), site_web, fill="#3498db")

    return badge