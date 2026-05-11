import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from enrollments.models import Enrollment
from .models import Payment

logger = logging.getLogger(__name__)

# Coordonnées de paiement
PAYMENT_INFO = {
    'mtn': {
        'number': '01 96 38 92 49',
        'name':   'CODJO Abel Jean Eudes',
        'logo':   '🟡',
        'label':  'MTN Mobile Money',
    },
    'moov': {
        'number': '01 95 51 17 61',
        'name':   'CODJO Abel Jean Eudes',
        'logo':   '🔵',
        'label':  'MOOV Money',
    },
}


# ─────────────────────────────────────────────────────────
#  CHECKOUT — Instructions + formulaire de confirmation
# ─────────────────────────────────────────────────────────
def checkout_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, status='pending')

    if request.session.get('enrollment_id') != enrollment.pk:
        return redirect('enrollments:create')

    error = None

    if request.method == 'POST':
        method     = request.POST.get('method', '').strip()
        phone_used = request.POST.get('phone_used', '').strip()

        if method not in ('mtn', 'moov'):
            error = "Veuillez choisir un réseau (MTN ou MOOV)."
        elif not phone_used:
            error = "Veuillez indiquer le numéro ayant effectué le paiement."
        else:
            # Créer le paiement en attente
            payment = Payment.objects.create(
                enrollment = enrollment,
                amount     = enrollment.tarif,
                method     = method,
                phone_used = phone_used,
                status     = 'pending',
            )

            # Stocker en session pour la page de reçu
            request.session['payment_id'] = payment.pk
            request.session.pop('enrollment_id', None)

            return redirect('payments:receipt', pk=payment.pk)

    return render(request, 'payments/checkout.html', {
        'enrollment':   enrollment,
        'payment_info': PAYMENT_INFO,
        'error':        error,
    })


# ─────────────────────────────────────────────────────────
#  REÇU — Page de confirmation + téléchargement
# ─────────────────────────────────────────────────────────
def receipt_view(request, pk):
    payment    = get_object_or_404(Payment, pk=pk)
    enrollment = payment.enrollment

    return render(request, 'payments/receipt.html', {
        'payment':    payment,
        'enrollment': enrollment,
    })


# ─────────────────────────────────────────────────────────
#  REÇU PDF — Version imprimable (même template, mode print)
# ─────────────────────────────────────────────────────────
def receipt_print_view(request, pk):
    payment    = get_object_or_404(Payment, pk=pk)
    enrollment = payment.enrollment

    return render(request, 'payments/receipt_print.html', {
        'payment':    payment,
        'enrollment': enrollment,
    })


# ─────────────────────────────────────────────────────────
#  ADMIN : Confirmer un paiement
# ─────────────────────────────────────────────────────────
def confirm_payment_view(request, pk):
    """Vue admin rapide pour confirmer un paiement."""
    if not request.user.is_staff:
        return HttpResponse("Accès refusé", status=403)

    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST' and payment.status == 'pending':
        payment.status       = 'confirmed'
        payment.confirmed_at = timezone.now()
        payment.save()

        payment.enrollment.activate_if_paid()

        if payment.enrollment.status == 'active':
            _send_sms_confirmation(payment.enrollment)

        logger.info(f"Paiement confirmé manuellement : {payment.receipt_number}")

    return redirect('/admin/payments/payment/')


# ─────────────────────────────────────────────────────────
#  SMS
# ─────────────────────────────────────────────────────────
def _send_sms_confirmation(enrollment):
    message = (
        f"Inscription confirmee ! {enrollment.full_name} "
        f"en {enrollment.level_serie} au Groupe La Certitude. "
        f"RDV le 1er juillet a EPP Gbegamey Sud. Tel: 96 38 92 49"
    )
    phones = [enrollment.phone]
    if enrollment.parent_phone:
        phones.append(enrollment.parent_phone)
    for phone in phones:
        logger.info(f"[SMS] → {phone} : {message}")
        # TODO : brancher API SMS étape 4