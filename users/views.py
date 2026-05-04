from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .forms import ApprenantRegisterForm, ParentRegisterForm, StudentForm, LoginForm
from .models import Student

User = get_user_model()


# ─────────────────────────────────────────────────────────
#  PAGE DE CHOIX : apprenant ou parent ?
# ─────────────────────────────────────────────────────────
def register_choice_view(request):
    """Page intermédiaire : choisir son profil avant de s'inscrire."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return render(request, 'users/register_choice.html')


# ─────────────────────────────────────────────────────────
#  INSCRIPTION APPRENANT
# ─────────────────────────────────────────────────────────
def register_apprenant_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    form = ApprenantRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Bienvenue {user.first_name} ! Votre compte apprenant a été créé.")
        return redirect('users:dashboard')

    return render(request, 'users/register_apprenant.html', {'form': form})


# ─────────────────────────────────────────────────────────
#  INSCRIPTION PARENT
# ─────────────────────────────────────────────────────────
def register_parent_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    form = ParentRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Bienvenue {user.first_name} ! Ajoutez maintenant votre (vos) enfant(s).")
        return redirect('users:add_child')

    return render(request, 'users/register_parent.html', {'form': form})


# ─────────────────────────────────────────────────────────
#  AJOUTER UN ENFANT (parent uniquement)
# ─────────────────────────────────────────────────────────
@login_required
def add_child_view(request):
    if not request.user.is_parent_role:
        return HttpResponseForbidden("Accès réservé aux parents.")

    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        child = form.save(commit=False)
        child.parent = request.user
        child.save()
        messages.success(request, f"{child.full_name} a été ajouté(e) avec succès.")

        # Continuer à ajouter ou aller au dashboard
        if 'add_another' in request.POST:
            return redirect('users:add_child')
        return redirect('users:dashboard')

    children = request.user.children.all()
    return render(request, 'users/add_child.html', {'form': form, 'children': children})


# ─────────────────────────────────────────────────────────
#  CONNEXION
# ─────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Bon retour, {user.first_name} !")
        return redirect(request.GET.get('next', 'users:dashboard'))

    return render(request, 'users/login.html', {'form': form})


# ─────────────────────────────────────────────────────────
#  DÉCONNEXION
# ─────────────────────────────────────────────────────────
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')


# ─────────────────────────────────────────────────────────
#  DASHBOARD — redirige selon le rôle
# ─────────────────────────────────────────────────────────
@login_required
def dashboard_view(request):
    user = request.user

    if user.is_apprenant:
        return _dashboard_apprenant(request, user)
    elif user.is_parent_role:
        return _dashboard_parent(request, user)
    elif user.is_prof:
        return _dashboard_prof(request, user)
    elif user.is_admin_role or user.is_staff:
        return redirect('/admin/')
    return redirect('home')


# ── Dashboard apprenant ──────────────────────────────────
def _dashboard_apprenant(request, user):
    WHATSAPP_LINKS = {
        '3eme': {
            'group_link': 'https://chat.whatsapp.com/LIEN_GROUPE_3EME',
            'prof_name':  'M. AGOSSOU Kévin',
            'prof_phone': '+22997000001',
        },
        '1ere': {
            'group_link': 'https://chat.whatsapp.com/LIEN_GROUPE_1ERE',
            'prof_name':  'M. HOUNKPATIN Théodore',
            'prof_phone': '+22997000002',
        },
        'tle': {
            'group_link': 'https://chat.whatsapp.com/LIEN_GROUPE_TLE',
            'prof_name':  'M. AHOUANSOU Martial',
            'prof_phone': '+22997000003',
        },
    }
    whatsapp_info = WHATSAPP_LINKS.get(user.level, {})

    try:
        enrollments = user.enrollments.select_related('course').prefetch_related('payments').all()
    except Exception:
        enrollments = []

    return render(request, 'users/dashboard_apprenant.html', {
        'user': user,
        'enrollments': enrollments,
        'whatsapp_info': whatsapp_info,
    })


# ── Dashboard parent ─────────────────────────────────────
def _dashboard_parent(request, user):
    children = user.children.prefetch_related('enrollments__course', 'enrollments__payments').all()
    return render(request, 'users/dashboard_parent.html', {
        'user': user,
        'children': children,
    })


# # ── Dashboard prof ───────────────────────────────────────
def _dashboard_prof(request, user):
    # Récupérer les apprenants du même niveau que la matière du prof
    try:
        from apps.enrollments.models import Enrollment
        enrollments = Enrollment.objects.filter(
            status='active'
        ).select_related('student', 'course')
    except Exception:
        enrollments = []

    return render(request, 'users/dashboard_prof.html', {
        'user': user,
        'enrollments': enrollments,
    })