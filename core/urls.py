from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',              views.home,         name='index'),
    path('a-propos/', views.about, name='about'), 
    path('galerie/',      views.galerie,      name='galerie'),
    path('temoignages/',  views.temoignages,  name='temoignages'),
]