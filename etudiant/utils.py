import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def generate_modern_qr(student):
    # Configuration
    site_web = "www.stepic-mada.com"
    verify_url = f"https://{site_web}/verify/{student.matricule}"
    
    # Données du QR
    qr_data = f"STUDENT_VERIFY:{student.matricule}|{site_web}"

    # 1. Création du QR Code (High Quality)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#2c3e50", back_color="white").convert('RGB')

    # 2. Création du Canevas (Largeur 400px pour un rendu propre)
    width, qr_height = qr_img.size
    canvas_height = qr_height + 180
    badge = Image.new('RGB', (width, canvas_height), 'white')
    draw = ImageDraw.Draw(badge)

    # 3. Design : Fond et bordures
    badge.paste(qr_img, (0, 0))
    
    # Ligne de séparation stylée
    draw.rectangle([10, qr_height, width-10, qr_height+2], fill="#3498db")

    # 4. Ajout des textes (Positionnement)
    # Note: Sur Render, utilisez le chemin complet si vous uploadez une police .ttf
    try:
        font_main = ImageFont.load_default() # Remplacez par un .ttf pour plus de style
    except:
        font_main = ImageFont.load_default()

    y_offset = qr_height + 20
    draw.text((20, y_offset), f"ID: {student.matricule}", fill="#e74c3c")
    draw.text((20, y_offset + 25), f"{student.nom.upper()} {student.prenom}", fill="#2c3e50")
    draw.text((20, y_offset + 50), f"Parcours: {student.parcours}", fill="#7f8c8d")
    draw.text((20, y_offset + 80), site_web, fill="#3498db")
    
    # Petit badge "VÉRIFIÉ" en bas
    draw.rectangle([width-100, canvas_height-30, width-10, canvas_height-10], fill="#2ecc71")
    draw.text((width-90, canvas_height-25), "OFFICIEL", fill="white")

    return badge