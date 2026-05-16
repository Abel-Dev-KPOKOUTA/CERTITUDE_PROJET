# resources/urls.py
from django.urls import path
from . import views

app_name = 'resources'
urlpatterns = [
    path('astuces/', views.tip_list, name='astuces'),
    path('astuce/<slug:slug>/', views.tip_detail, name='tip_detail'),
    path('cours/', views.course_list, name='cours'),
    path('cours/<slug:slug>/', views.course_detail, name='course_detail'),
]