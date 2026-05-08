from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('inscription/',            views.enrollment_create_view,  name='create'),
    path('inscription/<int:pk>/ok/', views.enrollment_success_view, name='success'),
]