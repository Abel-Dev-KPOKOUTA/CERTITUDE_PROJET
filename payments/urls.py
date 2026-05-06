from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('confirmation/<int:enrollment_id>/', views.confirmation_view, name='confirmation'),
]