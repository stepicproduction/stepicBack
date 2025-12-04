from rest_framework import serializers
from .models import Utilisateur

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta :
        model = Utilisateur
        fields = ['id', 'username', 'email', 'role', 'password', 'image']
        extra_kwargs = {
            'password' : {'write_only' :True, 'required' : False} #le mot de passe ne doit pas s'afficher dans la réponse
        }


    def create(self, validated_data):
        # create_user s’occupe de is_staff, is_superuser, is_active et du hash
        image = validated_data.pop("image", None)
        user =  Utilisateur.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "employe")
        )

        if image:
            user.image = image
            user.save()

        return user

        
    def update(self, instance, validated_data): #gestion du hashage lors de l'update
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)

        password = validated_data.get("password", None)
        if password :
            instance.set_password(password)

        image = validated_data.get("image", None)
        if image :
            instance.image = image

        instance.save()
        return instance
        