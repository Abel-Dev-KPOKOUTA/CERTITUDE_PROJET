from django.urls import path
from .import views

app_name = 'users'

urlpatterns = [
    # Choix du profil
    # path('inscription/',views.register_choice_view,name='register'),

    # # Inscription selon le rôle
    # path('inscription/apprenant/',views.register_apprenant_view,name='register_apprenant'),
    # path('inscription/parent/',views.register_parent_view,name='register_parent'),

    # # Gestion des enfants (parent)
    # path('mon-espace/ajouter-enfant/',views.add_child_view,name='add_child'),

    # # Auth
    # path('connexion/',views.login_view,name='login'),
    # path('deconnexion/',views.logout_view,name='logout'),

    # # Dashboard (redirige selon rôle)
    # path('mon-espace/',views.dashboard_view,name='dashboard'),
]