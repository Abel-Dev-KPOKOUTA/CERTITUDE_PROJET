from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Création transaction + redirection FedaPay
    path('paiement/<int:pk>/',          views.checkout_view,          name='checkout'),

    # FedaPay redirige l'utilisateur ici après paiement
    path('paiement/callback/<int:pk>/', views.payment_callback_view,  name='callback'),

    # Webhook FedaPay (notification serveur automatique)
    path('paiement/webhook/',           views.webhook_view,           name='webhook'),
]