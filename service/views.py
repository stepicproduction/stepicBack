from django.shortcuts import render
from .models import Service, Categorie
from .serializers import ServiceSerializer, CategorieSerializer
from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

import os
from google import genai
from rest_framework.decorators import api_view, permission_classes # (Vérifie si api_view est là)


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.image:
            print("Path stocké :", instance.image.name)
            print("URL :", default_storage.url(instance.image.name))

    @action(detail=False, methods=['get'], url_path='with_commande')
    def commande(self, request):
        categories = Categorie.objects.filter(button__iexact = "Commander")
        serialiezer = self.get_serializer(categories, many=True)
        return Response(serialiezer.data)
    
    @action(detail=False, methods=['get'], url_path='with_inscription')
    def inscription(self, request):
        categories = Categorie.objects.filter(button__iexact = "S'inscrire")
        serialiezer = self.get_serializer(categories, many=True)
        return Response(serialiezer.data)

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]


    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.image:
            print("Path stocké :", instance.image.name)
            print("URL :", default_storage.url(instance.image.name))

    @action(detail=False, methods=['get'], url_path='by_categorie/(?P<categorie_id>[^/.]+)')
    def by_categorie(self, request, categorie_id=None):
        """categorie_id = request.query_params.get('categorie_id')
        if not categorie_id:
            return Response({"error":"categorie_id est requis"}, status=400)
        offres = self.queryset.filter(categorie_id=categorie_id)"""
        offres = Service.objects.filter(categorie_id=categorie_id)
        serializer = self.get_serializer(offres, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='count')
    def total(self, request):
        nb_total = Service.objects.count()
        return Response({'total_services': nb_total})
    
    @action(detail=False, methods=['get'], url_path='with_inscription')
    def avec_inscription(self, request):
        offres = Service.objects.filter(button__iexact="S'inscrire")
        serializer = self.get_serializer(offres, many=True)
        return Response(serializer.data)
    
    #generation pdf de toutes les commandes
    @action(detail=False, methods=["get"], url_path="pdf_service")
    def pdf_inscription(self, request):
        service = Service.objects.all()

        html = render_to_string("liste_services.html", {
            "services": service,
        })

        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = f'inline; filename="service.pdf"'
        return response 
     
@api_view(['POST'])
@permission_classes([AllowAny])
def chat_assistant(request):
    user_message = request.data.get("message")
    
    if not user_message:
        return Response({"error": "Message vide"}, status=400)

    try:
        # 1. Extraction des offres et catégories de la base de données
        # On récupère tout pour que l'IA ait une vue d'ensemble
        categories = Categorie.objects.all()
        services = Service.objects.select_related('categorie').all()

        # 2. Construction d'un catalogue textuel pour l'IA
        catalogue_texte = "Voici nos offres actuelles chez STEPIC :\n"
        for cat in categories:
            catalogue_texte += f"\nCatégorie : {cat.nom}\n"
            offres_de_cette_cat = services.filter(categorie=cat)
            for s in offres_de_cette_cat:
                catalogue_texte += f"- {s.nom} : {s.description[:100]}...\n"

        # 3. Configuration des instructions système
        instructions = (
            "Tu es l'assistant de STEPIC. Ton rôle est de guider l'utilisateur sur notre site web. "
            "Voici le plan du site pour orienter les clients :\n"
            "- Onglet 'Services' ou 'Offres' : Pour voir toutes nos formations en détail.\n"
            "- Onglet 'Contact' : Pour nous envoyer un message via le formulaire ou voir notre numéro.\n"
            "- Section 'Actualités/Presse' : Pour lire nos derniers articles et événements.\n"
            "- Bouton Commander : Présent sur certaines offres pour passer une commande directe via un formulaire de commande.\n"
            "- Bouton 'S'inscrire' : Présent sur certaines offres pour s'inscrire directement via un formulaire d'inscription.\n\n"
            "CONSIGNES :\n"
            "1. Si l'utilisateur demande comment s'inscrire, dirige-le vers l'onglet 'Offres' pour choisir une offre.\n"
            "2. Si l'utilisateur demande comment passer une commande, dirige-le vers l'onglet 'Offres' pour choisir une offre ou bien sur le header, il y a un bouton Commander pour passer directement une commande.\n"
            "3. Si l'utilisateur a un problème spécifique, suggère le formulaire dans l'onglet 'Contact'.\n"
            "4. Si l'utilisateur veut des news, parle-lui de la section 'Presse'.\n"
            "5. Si l'utilisateur demande notre localisation, nous sommes à Tuléar Madagascar, Tanambao-I, ruelle n°2 derrière Supermaki ou dirige-le vers l'onglet Contact où il y a une carte de google Map'.\n"
            "6. Réponds toujours en 3 phrases maximum, avec enthousiasme."
        )

        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

        # 4. Envoi à Gemini
        response = client.models.generate_content(
            model='models/gemini-flash-latest',
            config={
                'system_instruction': instructions # On injecte le rôle ici
            },
            contents=f"CATALOGUE :\n{catalogue_texte}\n\nQUESTION CLIENT : {user_message}"
        )

        return Response({"reply": response.text})

    except Exception as e:
        error_str = str(e)
        # On vérifie si c'est une erreur de quota (429 ou "quota exceeded")
        if "429" in error_str or "quota" in error_str.lower() or "exhausted" in error_str.lower():
            return Response({
                "reply": "Je reçois beaucoup de messages en ce moment ! 🚀 Veuillez patienter quelques instants avant de me reposer votre question. Je serai de nouveau disponible dans une minute."
            }, status=200) # On renvoie 200 pour que le front l'affiche comme un message normal
        
        # Pour les autres types d'erreurs
        print(f"Erreur technique : {e}")
        return Response({"reply": "Désolé, j'ai une petite fatigue technique. Réessayez dans un instant !"}, status=200)