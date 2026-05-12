from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',              views.home,         name='index'),
    path('galerie/',      views.galerie,      name='galerie'),
    path('temoignages/',  views.temoignages,  name='temoignages'),
    path('astuces/', views.astuces , name='astuces'),
]