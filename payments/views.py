import fedapay
import json
import hmac
import hashlib
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages

from enrollments.models import Enrollment
from .models import Payment
from .utils import generate_receipt_pdf


# ── Configuration FedaPay ─────────────────────────────────
def _setup_fedapay():
    fedapay.api_key = settings.FEDAPAY_SECRET_KEY
    fedapay.api_base = (
        'https://sandbox-api.fedapay.com'
        if settings.FEDAPAY_ENV == 'sandbox'
        else 'https://api.fedapay.com'
    )


# ─────────────────────────────────────────────────────────
#  INITIER LE PAIEMENT FEDAPAY
# ─────────────────────────────────────────────────────────
@login_required
def initiate_payment_view(request, enrollment_id):
    """
    Crée une transaction FedaPay et redirige vers la
    page de paiement sécurisée.
    """
    enrollment = get_object_or_404(
        Enrollment, id=enrollment_id, student=request.user
    )

    if enrollment.is_fully_paid:
        messages.info(request, "Cette formation est déjà entièrement payée.")
        return redirect('users:dashboard')

    payment_mode   = request.GET.get('mode', 'complet')
    payment_method = request.GET.get('method', 'mtn')

    # Calcul du montant à payer maintenant
    if payment_mode == 'tranche' and int(enrollment.total_paid) == 0:
        amount = enrollment.course.first_tranche
    else:
        amount = enrollment.remaining

    _setup_fedapay()

    try:
        transaction = fedapay.Transaction.create(
            description=(
                f"Cours de renforcement {enrollment.course.get_level_display()} "
                f"— Groupe La Certitude 2026"
            ),
            amount=int(amount),
            currency={'iso': 'XOF'},
            callback_url=request.build_absolute_uri(
                f'/paiements/callback/{enrollment.id}/'
            ),
            customer={
                'firstname': request.user.first_name,
                'lastname':  request.user.last_name,
                'email':     request.user.email or f'{request.user.username}@lacertitude.bj',
                'phone_number': {
                    'number':  request.user.phone or '00000000',
                    'country': 'BJ',
                },
            },
        )

        # Sauvegarder le paiement en pending avec la référence FedaPay
        Payment.objects.create(
            enrollment=enrollment,
            amount=amount,
            method=payment_method,
            status='pending',
            reference=str(transaction.id),
        )

        # Rediriger vers la page de paiement FedaPay
        token       = transaction.generateToken()
        payment_url = token['url']
        return redirect(payment_url)

    except Exception as e:
        messages.error(request, f"Erreur lors de l'initiation du paiement : {str(e)}")
        return redirect('enrollments:checkout', course_id=enrollment.course.id)


# ─────────────────────────────────────────────────────────
#  CALLBACK FEDAPAY (retour apprenant après paiement)
# ─────────────────────────────────────────────────────────
@login_required
def payment_callback_view(request, enrollment_id):
    """
    FedaPay redirige l'apprenant ici après paiement.
    Paramètres GET : ?id=<transaction_id>&status=approved|declined|...
    """
    enrollment = get_object_or_404(
        Enrollment, id=enrollment_id, student=request.user
    )

    transaction_id = request.GET.get('id', '')
    feda_status    = request.GET.get('status', '')

    if transaction_id and feda_status == 'approved':
        _setup_fedapay()
        try:
            transaction = fedapay.Transaction.retrieve(transaction_id)
            if transaction.status == 'approved':
                payment = Payment.objects.filter(
                    enrollment=enrollment,
                    reference=transaction_id,
                    status='pending',
                ).first()

                if payment:
                    payment.status  = 'confirmed'
                    payment.paid_at = timezone.now()
                    payment.save()

                    # Activer l'inscription si paiement complet
                    if enrollment.is_fully_paid:
                        enrollment.status = 'active'
                        enrollment.save()

                    messages.success(
                        request,
                        "✅ Paiement confirmé avec succès ! "
                        "Votre inscription est maintenant active."
                    )
                    return redirect('payments:confirmation', enrollment_id=enrollment_id)

        except Exception as e:
            messages.error(request, f"Erreur de vérification : {str(e)}")

    elif feda_status in ('declined', 'canceled'):
        messages.error(
            request,
            "❌ Paiement annulé ou refusé. Veuillez réessayer."
        )

    return redirect('payments:confirmation', enrollment_id=enrollment_id)


# ─────────────────────────────────────────────────────────
#  WEBHOOK FEDAPAY (notification serveur → serveur)
# ─────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def fedapay_webhook_view(request):
    """
    FedaPay envoie une notification POST à cette URL.
    À configurer dans le dashboard FedaPay :
    https://votredomaine.com/paiements/webhook/
    """
    payload   = request.body
    signature = request.headers.get('X-FEDAPAY-SIGNATURE', '')

    # Vérification de signature (recommandée en production)
    webhook_secret = getattr(settings, 'FEDAPAY_WEBHOOK_SECRET', '')
    if webhook_secret:
        expected = hmac.new(
            webhook_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return HttpResponse(status=400)

    try:
        data  = json.loads(payload)
        event = data.get('name', '')
        entity = data.get('entity', {})

        if event == 'transaction.approved':
            transaction_id = str(entity.get('id', ''))
            amount         = Decimal(str(entity.get('amount', 0)))

            payment = Payment.objects.filter(
                reference=transaction_id,
                status='pending',
            ).first()

            if payment:
                payment.status  = 'confirmed'
                payment.paid_at = timezone.now()
                payment.save()

                enrollment = payment.enrollment
                if enrollment.is_fully_paid:
                    enrollment.status = 'active'
                    enrollment.save()

        return HttpResponse(status=200)

    except Exception:
        return HttpResponse(status=500)


# ─────────────────────────────────────────────────────────
#  PAGE DE CONFIRMATION
# ─────────────────────────────────────────────────────────
@login_required
def confirmation_view(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment, id=enrollment_id, student=request.user
    )

    # Dernier paiement confirmé
    payment = enrollment.payments.filter(
        status='confirmed'
    ).order_by('-created_at').first()

    # Si pas encore confirmé, prendre le dernier en date
    if not payment:
        payment = enrollment.payments.order_by('-created_at').first()

    WHATSAPP_LINKS = {
        '3eme':  {'group_link': 'https://chat.whatsapp.com/LIEN_3EME',  'prof_name': 'M. AGOSSOU Kévin',       'prof_phone': '+22997000001'},
        '1ereC': {'group_link': 'https://chat.whatsapp.com/LIEN_1EREC', 'prof_name': 'M. HOUNKPATIN Théodore',  'prof_phone': '+22997000002'},
        '1ereD': {'group_link': 'https://chat.whatsapp.com/LIEN_1ERED', 'prof_name': 'M. AZONHIHO Serge',       'prof_phone': '+22997000003'},
        'tleC':  {'group_link': 'https://chat.whatsapp.com/LIEN_TLEC',  'prof_name': 'M. AHOUANSOU Martial',    'prof_phone': '+22997000004'},
        'tleD':  {'group_link': 'https://chat.whatsapp.com/LIEN_TLED',  'prof_name': 'M. GBENOU Patrick',       'prof_phone': '+22997000005'},
    }
    whatsapp_info = WHATSAPP_LINKS.get(request.user.level, {})

    return render(request, 'payments/confirmation.html', {
        'enrollment':    enrollment,
        'payment':       payment,
        'whatsapp_info': whatsapp_info,
    })


# ─────────────────────────────────────────────────────────
#  TÉLÉCHARGER LE REÇU PDF
# ─────────────────────────────────────────────────────────
@login_required
def download_receipt_view(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment, id=enrollment_id, student=request.user
    )

    # Prendre tous les paiements confirmés
    payments = enrollment.payments.filter(status='confirmed').order_by('created_at')

    if not payments.exists():
        messages.error(request, "Aucun paiement confirmé pour cette inscription.")
        return redirect('users:dashboard')

    pdf_buffer = generate_receipt_pdf(enrollment, payments)

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"recu_lacertitude_{enrollment.id}.pdf",
        content_type='application/pdf',
    )