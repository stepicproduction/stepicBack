from django.contrib import admin
from .models import Categorie, Service

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "image")  # Champs visibles dans la liste
    list_editable = ("image",)       # Permet de modifier directement depuis la liste (optionnel)
    search_fields = ("nom",)
    
admin.site.register(Service)
# Register your models here.
