import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from django.conf import settings

def generate_modern_qr(student):
    # 1. Configuration des liens
    site_web = "www.stepic-mada.com"
    # L'URL de vérification qui sera développée plus tard
    verify_url = f"https://{site_web}/verify/{student.matricule}"
    
    # 2. Contenu textuel (Ce qui s'affiche au scan)
    # On utilise des majuscules et des séparateurs pour la clarté
    qr_payload = (
        f"--- STEPIC ---\n"
        f"SITE : {site_web}\n\n"
        f"MATRICULE : {student.matricule}\n"
        f"NOM : {student.nom.upper()} {student.prenom}\n"
        f"PARCOURS : {student.parcours.nom}\n" # Affiche 'Développement Web' au lieu d'un ID
        f"VERIFICATION EN LIGNE : {verify_url}\n"
    )

    # 3. Création du QR Code (Image)
    qr = qrcode.QRCode(
        version=None, # S'adapte automatiquement à la taille du texte
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=10,
        border=2,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)
    
    # Couleur sombre (#2c3e50) pour un look moderne
    qr_img = qr.make_image(fill_color="#2c3e50", back_color="white").convert('RGB')

    # 4. Insertion du logo au centre du QR
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

    # 5. Création du badge final (QR + Texte visuel en bas)
    width, qr_h_final = qr_img.size
    canvas_h = qr_h_final + 160
    badge = Image.new('RGB', (width, canvas_h), 'white')
    badge.paste(qr_img, (0, 0))
    
    draw = ImageDraw.Draw(badge)
    
    # Ligne de design bleue
    draw.rectangle([15, qr_h_final, width-15, qr_h_final+3], fill="#3498db")

    # Texte sur l'image (pour l'employé qui imprime)
    y = qr_h_final + 20
    draw.text((20, y), f"MATRICULE: {student.matricule}", fill="#e74c3c")
    draw.text((20, y + 30), f"{student.nom.upper()} {student.prenom}", fill="#2c3e50")
    draw.text((20, y + 60), f"PARCOURS: {student.parcours.nom}", fill="#7f8c8d")
    draw.text((20, y + 90), site_web, fill="#3498db")

    return badge