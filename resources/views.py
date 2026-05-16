# resources/views.py
from django.shortcuts import render, get_object_or_404
from .models import Tip, Course,Subject,Level

def tip_list(request):
    tips = Tip.objects.filter(is_published=True).select_related('subject', 'level')
    subjects = Subject.objects.all()
    levels = Level.objects.all()
    return render(request, 'resources/astuces.html', {
        'tips': tips,
        'subjects': subjects,
        'levels': levels,
    })

def tip_detail(request, slug):
    tip = get_object_or_404(Tip, slug=slug, is_published=True)
    return render(request, 'resources/tip_detail.html', {'tip': tip})

def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('subject', 'level')
    levels = Level.objects.all()
    return render(request, 'resources/cours.html', {
        'courses': courses,
        'levels': levels,
    })

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    return render(request, 'resources/course_detail.html', {'course': course})