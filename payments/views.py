import json
import logging
import uuid

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from enrollments.models import Enrollment
from .models import Payment

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
#  CHECKOUT — Page de paiement avec JS SDK FeexPay
# ─────────────────────────────────────────────────────────
def checkout_view(request, pk):
    """
    Affiche la page de paiement.
    Le SDK JS FeexPay gère la modal MTN/MOOV directement.
    """
    enrollment = get_object_or_404(Enrollment, pk=pk, status='pending')

    if request.session.get('enrollment_id') != enrollment.pk:
        return redirect('enrollments:create')

    # Créer ou récupérer le Payment pending
    payment, _ = Payment.objects.get_or_create(
        enrollment=enrollment,
        status='pending',
        defaults={'amount': enrollment.tarif},
    )

    # Générer un custom_id unique pour tracer la transaction
    if not payment.feexpay_reference:
        payment.feexpay_reference = f"LC-{enrollment.pk}-{uuid.uuid4().hex[:8].upper()}"
        payment.save(update_fields=['feexpay_reference'])

    return render(request, 'payments/checkout.html', {
        'enrollment': enrollment,
        'payment':    payment,
        'feexpay_id':    settings.FEEXPAY_SHOP_ID,
        'feexpay_token': settings.FEEXPAY_API_KEY,
        'feexpay_mode':  getattr(settings, 'FEEXPAY_MODE', 'SANDBOX'),
    })


# ─────────────────────────────────────────────────────────
#  SAVE REFERENCE — Appelé en AJAX après callback JS
# ─────────────────────────────────────────────────────────
def save_reference_view(request, pk):
    """
    Le JS du client envoie la référence FeexPay après paiement.
    On la sauvegarde et on répond avec l'URL de redirection.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data      = json.loads(request.body)
        reference = data.get('reference', '')
        status    = str(data.get('status', '')).upper()

        enrollment = get_object_or_404(Enrollment, pk=pk)
        payment    = enrollment.payments.filter(status='pending').first()

        if payment and reference:
            payment.feexpay_reference = reference
            payment.method = data.get('method', '')

            # Si le SDK confirme directement le succès
            if status in ('SUCCESSFUL', 'SUCCESS', 'COMPLETED', 'APPROVED'):
                payment.status  = 'confirmed'
                payment.paid_at = timezone.now()
                payment.save()
                enrollment.activate_if_paid()
                if enrollment.status == 'active':
                    _send_sms_confirmation(enrollment)
                request.session.pop('enrollment_id', None)
                return JsonResponse({
                    'success': True,
                    'redirect': f'/inscription/{enrollment.pk}/ok/',
                })
            else:
                payment.save()

        # Rediriger vers la page d'attente (webhook confirmera)
        return JsonResponse({
            'success': True,
            'redirect': f'/paiement/{enrollment.pk}/attente/',
        })

    except Exception as e:
        logger.error(f"save_reference error [{pk}]: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# ─────────────────────────────────────────────────────────
#  WAITING — Page d'attente
# ─────────────────────────────────────────────────────────
def waiting_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if enrollment.status == 'active':
        return redirect('enrollments:success', pk=pk)
    payment = enrollment.payments.order_by('-created_at').first()
    return render(request, 'payments/waiting.html', {
        'enrollment': enrollment,
        'payment':    payment,
    })


# ─────────────────────────────────────────────────────────
#  CHECK STATUS — Polling AJAX
# ─────────────────────────────────────────────────────────
def check_status_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    return JsonResponse({
        'status':   enrollment.status,
        'redirect': enrollment.status == 'active',
    })


# ─────────────────────────────────────────────────────────
#  WEBHOOK — FeexPay notifie notre serveur
# ─────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def webhook_view(request):
    try:
        data = json.loads(request.body)
        logger.info(f"FeexPay webhook: {data}")

        reference = data.get('reference', '') or data.get('custom_id', '')
        status    = str(data.get('status', '')).upper()

        if not reference:
            return HttpResponse(status=400)

        # Chercher par feexpay_reference ou custom_id (LC-{pk}-XXXXX)
        payment = (
            Payment.objects
            .filter(feexpay_reference=reference)
            .select_related('enrollment')
            .first()
        )

        # Fallback : chercher par custom_id encodé dans la référence
        if not payment and reference.startswith('LC-'):
            try:
                enrollment_pk = int(reference.split('-')[1])
                payment = (
                    Payment.objects
                    .filter(enrollment__pk=enrollment_pk, status='pending')
                    .select_related('enrollment')
                    .first()
                )
            except Exception:
                pass

        if not payment:
            logger.warning(f"Webhook: référence introuvable → {reference}")
            return HttpResponse(status=200)

        if status in ('SUCCESSFUL', 'SUCCESS', 'COMPLETED', 'APPROVED'):
            payment.status  = 'confirmed'
            payment.paid_at = timezone.now()
            payment.save()
            payment.enrollment.activate_if_paid()
            if payment.enrollment.status == 'active':
                _send_sms_confirmation(payment.enrollment)

        elif status in ('FAILED', 'CANCELLED', 'REJECTED'):
            payment.status = 'failed'
            payment.save()

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return HttpResponse(status=500)


# ─────────────────────────────────────────────────────────
#  SMS
# ─────────────────────────────────────────────────────────
def _send_sms_confirmation(enrollment):
    message = (
        f"Inscription confirmee ! {enrollment.full_name} "
        f"en {enrollment.level_serie} au Groupe La Certitude. "
        f"RDV le 1er juillet a EPP Gbegamey Sud. 96 38 92 49"
    )
    phones = [enrollment.phone]
    if enrollment.parent_phone:
        phones.append(enrollment.parent_phone)
    for phone in phones:
        logger.info(f"[SMS] → {phone} : {message}")
        # TODO : brancher API SMS étape 4