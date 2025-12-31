from django.shortcuts import render
from rest_framework import viewsets
from .models import Message
from .serializers import MessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import resend
import os

resend.api_key = os.environ.get("RESEND_API_KEY")
FROM_EMAIL = "STEPIC <admin@stepic-mada.com>"
ADMIN_EMAIL = os.environ.get("EMAIL_USER")

def send_response_email(message, body):
    """
    Envoie un email de réponse au client et met à jour le statut
    """
    try:
        subject = f"Réponse à votre message : {message.sujet}"
        html_content = f"""
        <html>
        <body>
            <p>Bonjour <strong>{message.nomClient}</strong>,</p>
            <p>{body}</p>
            <p>Cordialement,</p>
            <p>L'équipe STEPIC</p>
        </body>
        </html>
        """

        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": message.emailClient,
            "subject": subject,
            "html": html_content,
            "reply_to": ADMIN_EMAIL,
        })

        print("Email envoyé avec succès !")

    except Exception as e:
        print("Erreur lors de l'envoi de l'email :", e)
        raise e

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['put', 'patch'], url_path="lu")
    def lu(self, request, pk=None):
        try:
            message = self.get_object()
            message.statut = True
            message.save()
            return Response(
                {'message': 'Message lu ✅'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print("Erreur :", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['put', 'patch'], url_path="repondu")
    def repondu(self, request, pk=None):
        try:
            message = self.get_object()
            message.statut = True  # On garde comme "Lu"
            # Optionnel : tu peux ajouter un flag temporaire ou juste gérer côté front
            message.save()
            return Response({'message': 'Message répondu ✅'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'], url_path="repondre")
    def repondre(self, request, pk=None):
        message = self.get_object()
        body = request.data.get("body", "")
        if not body:
            return Response({"error": "Le corps du message est vide"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_response_email(message, body)
            message.statut = True  # Marquer comme "Répondu"
            message.save()
            return Response({"message": "Email envoyé et statut mis à jour ✅"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



