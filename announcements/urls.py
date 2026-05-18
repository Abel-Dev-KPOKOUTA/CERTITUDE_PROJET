from django.urls import path 
from . import views

app_name='announcements'

urlpatterns = [
    path('annonces/', views.annonces, name='annonces'),
    
]
