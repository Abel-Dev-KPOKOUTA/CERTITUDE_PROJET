from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('inscription/<int:course_id>/', views.checkout_view, name='checkout'),
]