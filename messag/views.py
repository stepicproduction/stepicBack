from django.shortcuts import render
from rest_framework import viewsets
from .models import Message
from .serializers import MessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

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


