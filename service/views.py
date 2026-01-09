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
import google.generativeai as genai
from rest_framework.decorators import api_view, permission_classes # (Vérifie si api_view est là)
from django.views.decorators.csrf import csrf_exempt
import json

api_key = os.environ.get('GEMINI_API_KEY')

if api_key:
    genai.configure(api_key=api_key)

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
     
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def chat_assistant(request):

    data = request.data

    # 🛡️ Si data est une string → on parse manuellement
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return Response(
                {"error": "Format JSON invalide"},
                status=400
            )

    user_message = data.get("message")

    if not user_message:
        return Response(
            {"error": "Message vide"},
            status=400
        )

    instruction = """
    Tu es l'assistant virtuel de STEPIC MADA (Madagascar).
    Identité : Professionnel, créatif et accueillant.
    Services : Communication, Design Graphique, Community Management, et Formations.
    Missions :
    - Expliquer les services
    - Guider sur la vérification des diplômes
    - Répondre en 3 phrases max
    """

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=instruction
        )

        response = model.generate_content(user_message)

        return Response({
            "reply": response.text or "Je suis là pour vous aider 😊"
        })

    except Exception as e:
        print("Erreur Gemini :", e)
        return Response(
            {"error": "L'assistant est momentanément indisponible"},
            status=500
        )



