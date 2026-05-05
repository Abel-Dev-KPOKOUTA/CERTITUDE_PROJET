from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course


@login_required
def course_list_view(request):
    """Liste de toutes les formations actives."""
    courses = Course.objects.filter(is_active=True)

    # Mettre en avant le cours correspondant au niveau de l'utilisateur
    user_level = getattr(request.user, 'level', None)

    return render(request, 'courses/list.html', {
        'courses':    courses,
        'user_level': user_level,
    })