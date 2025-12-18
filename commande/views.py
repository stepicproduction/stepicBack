from django.shortcuts import render
from rest_framework import viewsets
from .models import Commande
from .serializers import CommandeSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
import threading
from django.template.loader import render_to_string
from rest_framework.permissions import AllowAny
from django.utils.timezone import now, localtime
from django.templatetags.static import static
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import F, Func, Value
from django.db.models.functions import ExtractYear
from django.contrib.staticfiles import finders
import resend
import os

resend.api_key = os.environ.get("RESEND_API_KEY")
FROM_EMAIL = "STEPIC <onboarding@resend.dev>"
ADMIN_EMAIL = os.environ.get("EMAIL_USER")

def send_confirmation_email(commande):
    try:
        # Récupérer la catégorie et les services
        categorie = commande.categorie.nom if commande.categorie else "N/A"
        services = commande.service.all()

        # Construire la liste HTML des services
        services_html = "<ul>"
        for s in services:
            services_html += f"<li>{s.nom}</li>"
        services_html += "</ul>"

        # Contenu HTML de l'email
        subject = "Confirmation de commande - Votre demande est en cours de traitement"

        html_content = f"""
        <html>
        <body>
            <p>Bonjour <strong>{commande.nomClient} {commande.prenomClient}</strong>,</p>
            <p>Nous vous remercions sincèrement de votre commande passée le  {commande.dateCommande.strftime("%d-%m-%y à %H:%M:%S")} et elle est actuellement en cours de traitement et de préparation par notre Responsable !</p>
            <p>Récapitulatif du commande : </p>
            <p><strong>Catégorie choisie :</strong> {categorie}</p>
            <p><strong>Service(s) choisi(s) :</strong></p>
            {services_html}
            <p>Si vous avez des questions urgentes, n'hesitez surtout pas à répondre à ce courriel ou à nous contacter au 0342889956/0329320129. </p>
            <p>Cordialement,</p>
            <p>L'équipe STEPIC.</p>
        </body>
        </html>
        """

        # Création et envoi de l'email HTML

        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": commande.emailClient,
            "subject": subject,
            "html": html_content,
            "reply_to": ADMIN_EMAIL,
        })


        print("Email de confirmation envoyé avec succès !")

    except Exception as e:
        print("Erreur lors de l'envoi de l'email :", e)

def send_admin_notification(commande):
    """Avertit l'administrateur qu'une nouvelle inscription a été reçue."""
    try:
        categorie = commande.categorie.nom if commande.categorie else "N/A"
        services = commande.service.all()
        services_list = ", ".join([s.nom for s in services]) or "Aucun"

        subject = f"🆕 Nouvelle inscription reçue - {commande.nomClient} {commande.prenomClient}"

        html_content = f"""
        <html>
        <body>
            <h2>Nouvelle commande reçue sur Stepic ✅</h2>
            <p><strong>Nom :</strong> {commande.nomClient} {commande.prenomClient}</p>
            <p><strong>Email :</strong> {commande.emailClient}</p>
            <p><strong>Date :</strong> {commande.dateCommande.strftime("%d-%m-%Y à %H:%M:%S")}</p>
            <p><strong>Catégorie :</strong> {categorie}</p>
            <p><strong>Service(s) choisi(s) :</strong> {services_list}</p>
            <hr>
            <p>Connectez-vous à votre tableau d'administration pour valider ou refuser cette Commande.</p>
            <p><em>— Notification automatique Stepic</em></p>
        </body>
        </html>
        """

        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": ADMIN_EMAIL,
            "subject": subject,
            "html": html_content
        })

        print("📩 Email d’alerte envoyé à l’administrateur !")

    except Exception as e:
        print("❌ Erreur lors de l'envoi de l'email admin :", e)



class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer
    permission_classes = [AllowAny]

    #envoie de mail juste après la commande
    def perform_create(self, serializer):
        commande = serializer.save()
        threading.Thread(target=send_confirmation_email, args=(commande,), daemon=True).start()
        threading.Thread(target=send_admin_notification, args=(commande,), daemon=True).start()

    #nombres total des commandes
    @action(detail=False, methods=['get'], url_path='count')
    def total(self, request):
        nb_total = Commande.objects.count()
        return Response({'total_commande': nb_total})
    
    #listes des commandes par mois
    @action(detail=False, methods=['get'], url_path='by_month')
    def par_mois(self, request):
        annee = request.query_params.get('annee')

        if annee is None:
            annee = timezone.now().year
        else:
            annee = int(annee)

        commandes = (
            Commande.objects.filter(dateCommande__year=annee)
            .annotate(mois=ExtractMonth('dateCommande'))
            .values('mois')
            .annotate(total=Count('id'))
        )

        nom_mois = ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre",
                    "Octobre", "Novembre", "Décembre"]
        
        data = []
        for i, nom in enumerate(nom_mois, start=1):
            nb = next((c["total"] for c in commandes if c["mois"] == i), 0)
            data.append({
                "libelle": nom,
                "nb_commande": nb
            })

        return Response({"annee": annee, "commandes": data})
    
     #api pour retourner les dates qui a eu lieu pendant les commandes
    @action(detail=False, methods=['get'], url_path='available_years')
    def available_years(self, request):
        """
        Retourne toutes les années où il y a eu au moins une inscription.
        """
        years = (
            Commande.objects
            .annotate(year=ExtractYear('dateCommande'))
            .values_list('year', flat=True)
            .distinct()
            .order_by('-year')
        )
        return Response({"years": list(years)})

    #listes des commandes par an
    @action(detail=False, methods=['get'], url_path='by_year')
    def filter_by_year(self, request):
        """
        Retourne toutes les inscriptions pour une année donnée.
        Paramètre GET : ?annee=2025
        """
        annee = request.query_params.get('annee')

        if annee is None:
            annee = timezone.now().year
        else:
            try:
                annee = int(annee)
            except ValueError:
                return Response({"error": "Année invalide"}, status=400)

        commandes = Commande.objects.filter(dateCommande__year=annee)

        # Sérialisation
        serializer = self.get_serializer(commandes, many=True)
        return Response({
            "annee": annee,
            "commandes": serializer.data
        })
    
    #validation d'une commande
    @action(detail=True, methods=['patch', 'put', 'post'], url_path='valider')
    def valider_commande(self, request, pk=None):
        try:
            commande = self.get_object()
            commande.statut = True
            commande.save()

            #threading.Thread(target=send_confirmation_email, args=(commande,)).start()

            return Response(
                {'message': 'Commande validée et email envoyé en arrière-plan ✅'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print("Erreur lors de la validation :", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #previsualisation de reçu d'une commande    
    @action(detail=True, methods=["get"], url_path="preview")
    def preview_recu(self, request, pk=None):
        commande = self.get_object()
        recu_number = f"REC-{commande.dateCommande.strftime('%Y%m%d')}-{commande.id:04d}"
        services = commande.service.all()

        return render(request, "recu.html", {
            "type" : "RECU DE COMMANDE",
            "object": commande,
            "services": services,
            "logo_url": request.build_absolute_uri(static("images/stepic_logo.jpg")),
            "now": localtime(now()),
            "recu_number": recu_number,
        })
    
    #génération de pdf d'une commande
    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf_recu(self, request, pk=None):
        commande = self.get_object()
        recu_number = f"REC-{commande.dateCommande.strftime('%Y%m%d')}-{commande.id:04d}"
        services = commande.service.all()

        logo_path_local = finders.find("images/stepic_logo.jpg")

        if logo_path_local:
        # Remplace les backslashes par des slashes pour le format d'URL
            logo_url_for_pdf = 'file://' + logo_path_local.replace('\\', '/')
        else:
        # Solution de repli, même si elle a échoué via HTTP
            logo_url_for_pdf = request.build_absolute_uri(static("images/stepic_logo.jpg"))

        html = render_to_string("recu.html", {
            "type" : "RECU DE COMMANDE",
            "object": commande,
            "services": services,
            #"logo_url": request.build_absolute_uri(static("images/stepic_logo.jpg")),
            "logo_url": logo_url_for_pdf,
            "now": localtime(now()),
            "recu_number": recu_number,
        })

        pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = f'inline; filename="recu_{pk}.pdf"'
        return response
    
    #generation pdf de toutes les commandes
    @action(detail=False, methods=["get"], url_path="pdf_commande")
    def pdf_inscription(self, request):
        commande = Commande.objects.all()

        html = render_to_string("liste_commandes.html", {
            "commandes": commande,
        })

        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = f'inline; filename="commande.pdf"'
        return response    


