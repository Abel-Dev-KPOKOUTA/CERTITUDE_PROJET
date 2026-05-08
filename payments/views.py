import json
import logging

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from enrollments.models import Enrollment
from .models import Payment

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
#  HELPER : configure FedaPay (import lazy)
# ─────────────────────────────────────────────────────────
def _get_fedapay():
    """Importe et configure fedapay à la demande — évite l'erreur au démarrage."""
    import fedapay
    fedapay.api_key     = settings.FEDAPAY_SECRET_KEY
    fedapay.environment = getattr(settings, 'FEDAPAY_ENVIRONMENT', 'sandbox')
    return fedapay


# ─────────────────────────────────────────────────────────
#  CHECKOUT
# ─────────────────────────────────────────────────────────
def checkout_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, status='pending')

    if request.session.get('enrollment_id') != enrollment.pk:
        return redirect('enrollments:create')

    payment, _ = Payment.objects.get_or_create(
        enrollment=enrollment,
        status='pending',
        defaults={'amount': enrollment.tarif},
    )

    try:
        feda = _get_fedapay()

        callback_url = request.build_absolute_uri(
            f'/paiement/callback/{enrollment.pk}/'
        )

        transaction = feda.Transaction.create({
            'description': (
                f'La Certitude — {enrollment.full_name} — {enrollment.level_serie}'
            ),
            'amount':   int(enrollment.tarif),
            'currency': {'iso': 'XOF'},
            'callback_url': callback_url,
            'customer': {
                'firstname': enrollment.first_name,
                'lastname':  enrollment.last_name,
                'phone_number': {
                    'number':  enrollment.contact_phone.replace(' ', ''),
                    'country': 'BJ',
                }
            }
        })

        token_data   = transaction.generateToken()
        redirect_url = token_data['url']

        payment.fedapay_transaction_id = str(transaction.id)
        payment.fedapay_token          = token_data.get('token', '')
        payment.save()

        return redirect(redirect_url)

    except Exception as e:
        logger.error(f"FedaPay checkout error (enrollment {pk}): {e}")
        return render(request, 'payments/checkout_error.html', {
            'enrollment': enrollment,
            'error':      str(e),
        })


# ─────────────────────────────────────────────────────────
#  CALLBACK — FedaPay redirige l'utilisateur ici
# ─────────────────────────────────────────────────────────
def payment_callback_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)

    try:
        feda    = _get_fedapay()
        payment = enrollment.payments.filter(status='pending').first()

        if payment and payment.fedapay_transaction_id:
            transaction = feda.Transaction.retrieve(
                int(payment.fedapay_transaction_id)
            )
            _process_transaction(transaction, enrollment, payment)

    except Exception as e:
        logger.error(f"FedaPay callback error (enrollment {pk}): {e}")

    if enrollment.status == 'active':
        request.session.pop('enrollment_id', None)
        return redirect('enrollments:success', pk=enrollment.pk)

    return render(request, 'payments/pending.html', {'enrollment': enrollment})


# ─────────────────────────────────────────────────────────
#  WEBHOOK — Notification automatique FedaPay
# ─────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def webhook_view(request):
    payload = request.body

    webhook_secret = getattr(settings, 'FEDAPAY_WEBHOOK_SECRET', '')
    if webhook_secret:
        try:
            feda       = _get_fedapay()
            sig_header = request.META.get('HTTP_X_FEDAPAY_SIGNATURE', '')
            feda.Webhook.constructEvent(payload, sig_header, webhook_secret)
        except Exception as e:
            logger.warning(f"Webhook signature invalide : {e}")
            return HttpResponse(status=400)

    try:
        data       = json.loads(payload)
        event_name = data.get('name', '')
        logger.info(f"FedaPay webhook reçu : {event_name}")

        if event_name in ('transaction.approved', 'transaction.completed'):
            entity         = data.get('data', {}).get('object', {})
            transaction_id = str(entity.get('id', ''))

            payment = (
                Payment.objects
                .filter(fedapay_transaction_id=transaction_id)
                .select_related('enrollment')
                .first()
            )
            if payment:
                _process_transaction_data(entity, payment.enrollment, payment)

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Webhook processing error : {e}")
        return HttpResponse(status=500)


# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────
def _process_transaction(transaction, enrollment, payment):
    status = str(getattr(transaction, 'status', '')).lower()
    if status in ('approved', 'completed'):
        payment.status  = 'confirmed'
        payment.paid_at = timezone.now()
        payment.save()
        enrollment.activate_if_paid()
        if enrollment.status == 'active':
            _send_sms_confirmation(enrollment)
    elif status == 'declined':
        payment.status = 'failed'
        payment.save()


def _process_transaction_data(entity, enrollment, payment):
    status = str(entity.get('status', '')).lower()
    if status in ('approved', 'completed'):
        payment.status  = 'confirmed'
        payment.paid_at = timezone.now()
        payment.save()
        enrollment.activate_if_paid()
        if enrollment.status == 'active':
            _send_sms_confirmation(enrollment)
    elif status == 'declined':
        payment.status = 'failed'
        payment.save()


def _send_sms_confirmation(enrollment):
    message = (
        f"Inscription confirmee ! {enrollment.full_name} est inscrit(e) "
        f"en {enrollment.level_serie} au Groupe La Certitude. "
        f"RDV le 1er juillet a l'EPP Gbegamey Sud. Tel: 96 38 92 49"
    )
    phones = [enrollment.phone]
    if enrollment.parent_phone:
        phones.append(enrollment.parent_phone)
    for phone in phones:
        _dispatch_sms(phone, message)


def _dispatch_sms(phone, message):
    """Point d'entrée SMS — à brancher à l'étape 4."""
    logger.info(f"[SMS] → {phone} : {message}")