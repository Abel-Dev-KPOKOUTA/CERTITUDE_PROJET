from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from enrollments.models import Enrollment


@login_required
def confirmation_view(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment, id=enrollment_id, student=request.user
    )
    payment = enrollment.payments.order_by('-created_at').first()

    # Lien WhatsApp selon le niveau
    WHATSAPP_LINKS = {
        '3eme':  {'group_link': 'https://chat.whatsapp.com/LIEN_3EME',  'prof_name': 'M. AGOSSOU Kévin'},
        '1ereC': {'group_link': 'https://chat.whatsapp.com/LIEN_1EREC', 'prof_name': 'M. HOUNKPATIN Théodore'},
        '1ereD': {'group_link': 'https://chat.whatsapp.com/LIEN_1ERED', 'prof_name': 'M. AZONHIHO Serge'},
        'tleC':  {'group_link': 'https://chat.whatsapp.com/LIEN_TLEC',  'prof_name': 'M. AHOUANSOU Martial'},
        'tleD':  {'group_link': 'https://chat.whatsapp.com/LIEN_TLED',  'prof_name': 'M. GBENOU Patrick'},
    }
    whatsapp_info = WHATSAPP_LINKS.get(request.user.level, {})

    return render(request, 'payments/confirmation.html', {
        'enrollment':    enrollment,
        'payment':       payment,
        'whatsapp_info': whatsapp_info,
    })