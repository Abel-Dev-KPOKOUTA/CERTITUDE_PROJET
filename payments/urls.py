from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Page de paiement (JS SDK FeexPay)
    path('paiement/<int:pk>/',              views.checkout_view,       name='checkout'),

    # AJAX : sauvegarde la référence après callback JS
    path('paiement/<int:pk>/reference/',    views.save_reference_view, name='save_reference'),

    # Page d'attente
    path('paiement/<int:pk>/attente/',      views.waiting_view,        name='waiting'),

    # Polling AJAX
    path('paiement/<int:pk>/statut/',       views.check_status_view,   name='check_status'),

    # Webhook FeexPay
    path('paiement/webhook/',               views.webhook_view,        name='webhook'),
]