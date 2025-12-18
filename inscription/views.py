from django.shortcuts import render
from rest_framework import viewsets
from .models import Inscription
from .serializers import InscriptionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import ExtractMonth
from django.db.models import Count, Q  
from django.utils import timezone
from service.models import Service
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
FROM_EMAIL = "STEPIC <contact@stepic-mada.com>"
ADMIN_EMAIL = os.environ.get("EMAIL_USER")


def send_confirmation_email(inscription):
    try:
        categorie = inscription.categorie.nom if inscription.categorie else "N/A"
        services = inscription.service.all()

        # Construire la liste HTML des services
        services_html = "<ul>"
        for s in services:
            services_html += f"<li>{s.nom}</li>"
        services_html += "</ul>"

        # Contenu HTML de l'email
        subject = "Bienvenu ! Votre inscription est en cours de validation"
        html_content = f"""
        <html>
        <body>
            <p>Bonjour <Strong>{inscription.nomClient} {inscription.prenomClient}</strong>,</p>
            <p>Votre inscription du {inscription.dateInscription.strftime("%d-%m-%y à %H:%M:%S")} a été bien reçue avec succès et est actuellement en cours de traitement par notre Responsable !</p>
            <p>Résumé : </p>
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
            "to": inscription.emailClient,
            "subject": subject,
            "html": html_content,
            "reply_to": ADMIN_EMAIL,
        })

        print("Email de confirmation envoyé avec succès !")

    except Exception as e:
        print("Erreur lors de l'envoi de l'email :", e)


def send_admin_notification(inscription):
    """Avertit l'administrateur qu'une nouvelle inscription a été reçue."""
    try:
        categorie = inscription.categorie.nom if inscription.categorie else "N/A"
        services = inscription.service.all()
        services_list = ", ".join([s.nom for s in services]) or "Aucun"

        subject = f"🆕 Nouvelle inscription reçue - {inscription.nomClient} {inscription.prenomClient}"

        html_content = f"""
        <html>
        <body>
            <h2>Nouvelle inscription reçue sur Stepic ✅</h2>
            <p><strong>Nom :</strong> {inscription.nomClient} {inscription.prenomClient}</p>
            <p><strong>Email :</strong> {inscription.emailClient}</p>
            <p><strong>Date :</strong> {inscription.dateInscription.strftime("%d-%m-%Y à %H:%M:%S")}</p>
            <p><strong>Catégorie :</strong> {categorie}</p>
            <p><strong>Service(s) choisi(s) :</strong> {services_list}</p>
            <hr>
            <p>Connectez-vous à votre tableau d'administration pour valider ou refuser cette inscription.</p>
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


class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [AllowAny]

    #envoie de l'email juste après l'inscription
    def perform_create(self, serializer):
        inscription = serializer.save()

        print("🔴 Début du processus d'envoi d'e-mail (Synchrone) pour le débogage.")

        threading.Thread(target=send_confirmation_email, args=(inscription,), daemon=True).start()
        threading.Thread(target=send_admin_notification, args=(inscription,), daemon=True).start()

        print("🟢 Fin du processus d'envoi d'e-mail (Synchrone).")

    @action(detail=False, methods=['get'], url_path='count')
    def totalInscritpion(self, request):
        nb_total = Inscription.objects.count()
        return Response({'total_inscription': nb_total })
    
    #retourner l'évolution des inscriptions par mois
    @action(detail=False, methods=['get'], url_path='by_month')
    def evolution_par_mois(self, request):
        annee = request.query_params.get('annee')

        if annee is None:
            annee = timezone.now().year
        else :
            annee = int(annee)

        inscriptions = (
            Inscription.objects.filter(dateInscription__year=annee)
            .annotate(mois=ExtractMonth('dateInscription'))
            .values('mois')
            .annotate(total=Count('id'))
        )

        nom_mois = ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre",
                    "Octobre", "Novembre", "Décembre"]
        
        data = []
        for i, nom in enumerate(nom_mois, start=1):
            nb = next((c["total"] for c in inscriptions if c["mois"] == i), 0)
            data.append({
                "libelle": nom,
                "nb_inscription": nb
            })

        return Response({"annee": annee, "inscriptions": data})
    
    #api pour retourner les dates qui a eu lieu pendant les inscriptions
    @action(detail=False, methods=['get'], url_path='available_years')
    def available_years(self, request):
        """
        Retourne toutes les années où il y a eu au moins une inscription.
        """
        years = (
            Inscription.objects
            .annotate(year=ExtractYear('dateInscription'))
            .values_list('year', flat=True)
            .distinct()
            .order_by('-year')
        )
        return Response({"years": list(years)})
    
    #retourner les listes des inscriptions par an
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

        inscriptions = Inscription.objects.filter(dateInscription__year=annee)

        # Sérialisation
        serializer = self.get_serializer(inscriptions, many=True)
        return Response({
            "annee": annee,
            "inscriptions": serializer.data
        })
    
    #liste des inscriptions par service
    @action(detail=False, methods=['get'], url_path='by_service')
    def par_service(self, request):
        services_concerne = Service.objects.filter(button__iexact="S'inscrire")

        stats = (
            Inscription.objects.filter(service__in=services_concerne)
            .values('service__nom')
            .annotate(nb_inscriptions=Count('id'))
            .order_by('service__nom')
        )

        data = [
            {"service": s["service__nom"], "nbInscriptions": s["nb_inscriptions"]}
            for s in stats
        ]

        return Response(data)
    
    #validation d'une inscription
    @action(detail=True, methods=['patch', 'put', 'post'], url_path='valider')
    def valider_commande(self, request, pk=None):
        try:
            inscription = self.get_object()
            inscription.statut = True
            inscription.save()

            #threading.Thread(target=send_confirmation_email, args=(inscription,)).start()

            return Response(
                {'message': 'Inscription validée et email envoyé en arrière-plan ✅'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print("Erreur lors de la validation :", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    #listes des inscriptions par service spécifique
    @action(detail=False, methods=['get'], url_path='count-by-service')
    def count_by_service(self, request):

        services = (
            Service.objects.filter(
                button__iexact="S'inscrire"
            )
            .filter(
                Q(nom__icontains="française")
                | Q(nom__icontains="anglaise")
                | Q(nom__icontains="allemande")
                | Q(nom__icontains="chinoise")
                | Q(nom__icontains="informatique")
            )
            .annotate(nb_inscriptions=Count('inscriptions'))
            .values('nom', 'nb_inscriptions')
        )

            # Reformater pour ton frontend
        data = [
            {"name": s["nom"], "value": s["nb_inscriptions"]}
            for s in services
        ]

        return Response({"dataServices": data})
    
    #prévisualiser le réçu d'inscription
    @action(detail=True, methods=["get"], url_path="preview")
    def preview_recu(self, request, pk=None):
        inscription = self.get_object()
        recu_number = f"REC-{inscription.dateInscription.strftime('%Y%m%d')}-{inscription.id:04d}"
        services = inscription.service.all()

        return render(request, "recu.html", {
            "type" : "RECU D'INSCRIPTION",
            "object": inscription,
            "services": services,
            "logo_url": request.build_absolute_uri(static("images/stepic_logo.jpg")),
            "now": localtime(now()),
            "recu_number": recu_number,
        })
    
    @action(detail=False, methods=["get"], url_path="preview_liste")
    def preview_liste(self, request):
        inscription = Inscription.objects.all()

        return render(request, "liste_inscriptions.html", {
            "inscriptions": inscription,
        })
    
    #génération d'un reçu de chaque inscription
    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf_recu(self, request, pk=None):
        inscription = self.get_object()
        recu_number = f"REC-{inscription.dateInscription.strftime('%Y%m%d')}-{inscription.id:04d}"
        services = inscription.service.all()

        logo_path_local = finders.find("images/stepic_logo.jpg")

        if logo_path_local:
        # Remplace les backslashes par des slashes pour le format d'URL
            logo_url_for_pdf = 'file://' + logo_path_local.replace('\\', '/')
        else:
        # Solution de repli, même si elle a échoué via HTTP
            logo_url_for_pdf = request.build_absolute_uri(static("images/stepic_logo.jpg"))

        html = render_to_string("recu.html", {
            "type" : "RECU D'INSCRIPTION",
            "object": inscription,
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
    
    #generation pdf de toutes les inscriptions
    @action(detail=False, methods=["get"], url_path="pdf_inscription")
    def pdf_inscription(self, request):
        inscription = Inscription.objects.all()

        html = render_to_string("liste_inscriptions.html", {
            "inscriptions": inscription,
        })

        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = f'inline; filename="inscription.pdf"'
        return response