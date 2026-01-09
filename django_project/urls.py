"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from utilisateur.views import UtilisateurViewSet
from service.views import ServiceViewSet
from service.views import CategorieViewSet
from service.views import chat_assistant
from inscription.views import InscriptionViewSet
from commande.views import CommandeViewSet
from actualites.views import BlogViewSet
from messag.views import MessageViewSet
from project.views import ProjetViewSet
from about.views import AboutViewSet
from showreel.views import ShowreelViewSet
from temoignage.views import TemoignageViewSet
from presse.views import PresseViewSet
from equipe.views import EquipeModelViewSet
from etudiant.views import EtudiantViewSet

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)

router = routers.DefaultRouter()
router.register(r"utilisateurs", UtilisateurViewSet, basename="utilisateur")
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"categories", CategorieViewSet, basename="categorie")
router.register(r"inscriptions", InscriptionViewSet, basename="inscription")
router.register(r"commandes", CommandeViewSet, basename="commande")
router.register(r"actualites", BlogViewSet, basename="actualite")
router.register(r"messages", MessageViewSet, basename="message")
router.register(r"projets", ProjetViewSet, basename="projet")
router.register(r"about", AboutViewSet, basename="about")
router.register(r"showreels", ShowreelViewSet, basename="showreel")
router.register(r"temoignages", TemoignageViewSet, basename="temoignage")
router.register(r"presses", PresseViewSet, basename="presse")
router.register(r"equipes", EquipeModelViewSet, basename="equipe")
router.register(r"etudiants", EtudiantViewSet, basename="etudiant")



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/chat-assistant/', chat_assistant, name='chat-assistant'), # Route pour l'IA
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
