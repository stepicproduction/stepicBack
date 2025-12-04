from django.shortcuts import render
from rest_framework import viewsets
from .models import Utilisateur
from .serializers import UtilisateurSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='user_connected')
    def user_connected(self, request):
        user = request.user
        image_url = request.build_absolute_uri(user.image.url) if user.image else None

        return Response({
            "status": "ok",
            "user": user.username,
            "role": user.role,
            "image": image_url,
            "email": user.email,
            "id": user.id,
        })

    @action(detail=True, methods=['post'], url_path='changer-mdp')
    def changePassword(self, request, pk=None):
        user = self.get_object()

        print("Données reçues de la requête:", request.data)

        ancien_mdp = request.data.get('ancien_mdp')
        nouveau_mdp = request.data.get('nouveau_mdp')

        print(f"Ancien MDP: {ancien_mdp}, Nouveau MDP: {nouveau_mdp}")

        if not user.check_password(ancien_mdp):
            return Response(
                {
                    "ancien_mdp" : ["Le mot de passe actuel est incorrect"]
                },status=status.HTTP_400_BAD_REQUEST
            )
        
        if not nouveau_mdp or len(nouveau_mdp) < 8 :
            return Response(
                {
                    "nouveau_mdp" : ["Le nouveau mot de passe est trop court"]
                },status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(nouveau_mdp)
        user.save()
        return Response({'status': 'Mot de passe mis à jour'}, status=status.HTTP_200_OK)
