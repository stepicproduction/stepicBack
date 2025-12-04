# utilisateur/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Informations supplémentaires", {
            "fields" : ("role", "image")
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets +  (
        ("Informations supplémentaires", {
            "fields" : ("role", "image")
        }),
    )

    def save_model(self, request, obj, form, change):
        # Cette condition vérifie si le mot de passe a été modifié 
        # (c'est-à-dire s'il est un texte brut dans le formulaire)
        if obj.pk and not obj.password.startswith('pbkdf2'):
            obj.set_password(obj.password)
        elif not obj.pk: # Pour la création
             obj.set_password(obj.password)
             
        super().save_model(request, obj, form, change)

admin.site.register(Utilisateur, CustomUserAdmin)