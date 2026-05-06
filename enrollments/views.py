from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from courses.models import Course
from .models import Enrollment
from payments.models import Payment


@login_required
def checkout_view(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # Vérifier si déjà inscrit
    existing = Enrollment.objects.filter(
        student=request.user, course=course
    ).first()
    if existing:
        messages.info(request, "Vous êtes déjà inscrit à cette formation.")
        return redirect('payments:confirmation', enrollment_id=existing.id)

    if request.method == 'POST':
        payment_mode   = request.POST.get('payment_mode', 'complet')
        payment_method = request.POST.get('payment_method', 'mtn')

        # Calcul du montant
        if payment_mode == 'tranche':
            amount = course.first_tranche
        else:
            amount = int(course.price)

        # Créer l'inscription
        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course,
            status='pending',
        )

        # Créer le paiement
        Payment.objects.create(
            enrollment=enrollment,
            amount=amount,
            method=payment_method,
            status='pending',
        )

        messages.success(
            request,
            f"✅ Inscription enregistrée ! Votre paiement est en attente de validation."
        )
        return redirect('payments:confirmation', enrollment_id=enrollment.id)

    return render(request, 'enrollments/checkout.html', {
        'course': course,
    })