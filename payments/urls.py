from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Page de paiement (instructions + formulaire de confirmation)
    path('paiement/<int:pk>/',         views.checkout_view,      name='checkout'),

    # Reçu après paiement déclaré
    path('recu/<int:pk>/',             views.receipt_view,       name='receipt'),

    # Version imprimable du reçu
    path('recu/<int:pk>/imprimer/',    views.receipt_print_view, name='receipt_print'),

    # Confirmation admin rapide
    path('paiement/<int:pk>/confirmer/', views.confirm_payment_view, name='confirm'),
]