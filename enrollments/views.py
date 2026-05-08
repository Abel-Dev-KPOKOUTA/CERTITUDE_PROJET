from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Enrollment
from .forms import EnrollmentForm


# ─────────────────────────────────────────────────────────
#  FORMULAIRE D'INSCRIPTION
# ─────────────────────────────────────────────────────────
def enrollment_create_view(request):
    """
    Affiche et traite le formulaire d'inscription.
    Après soumission valide → crée Enrollment (pending) → redirige vers paiement.
    """
    # Pré-remplir le niveau si passé en GET (?niveau=3eme)
    initial = {}
    niveau_param = request.GET.get('niveau')
    if niveau_param in ['3eme', '1ere', 'tle']:
        initial['level'] = niveau_param

    form = EnrollmentForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        enrollment = form.save(commit=False)
        enrollment.status = 'pending'
        enrollment.save()

        # On stocke l'ID en session pour le récupérer sur la page de paiement
        request.session['enrollment_id'] = enrollment.pk

        return redirect('payments:checkout', pk=enrollment.pk)

    return render(request, 'enrollments/enroll.html', {
        'form':   form,
        'tarifs': {'3eme': 11_500, '1ere': 12_500, 'tle': 15_500},
    })


# ─────────────────────────────────────────────────────────
#  CONFIRMATION (page de succès après webhook FedaPay)
# ─────────────────────────────────────────────────────────
def enrollment_success_view(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    return render(request, 'enrollments/success.html', {'enrollment': enrollment})