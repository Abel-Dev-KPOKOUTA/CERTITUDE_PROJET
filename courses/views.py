from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course


@login_required
def course_list_view(request):
    courses = Course.objects.filter(is_active=True)
    user_level = getattr(request.user, 'level', None)

    for course in courses:
        course.is_recommended = (course.level == user_level)

    # Cours où l'utilisateur est déjà inscrit
    try:
        enrolled_ids = request.user.enrollments.values_list('course_id', flat=True)
    except Exception:
        enrolled_ids = []

    return render(request, 'courses/list.html', {
        'courses':         courses,
        'enrolled_courses': enrolled_ids,
    })