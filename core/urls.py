from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',              views.home,         name='index'),
    path('a-propos/', views.about, name='about'), 
    path('galerie/',      views.galerie,      name='galerie'),
    path('temoignages/',  views.temoignages,  name='temoignages'),
    path('programme-2026/', views.programme_2026, name='programme_2026'),
    path('edition-2025/', views.edition_2025, name='edition_2025'),
    path('epreuves/', views.epreuves, name='epreuves'),
    path('soutien-scolaire/', views.soutien_scolaire, name='soutien_scolaire'),
]