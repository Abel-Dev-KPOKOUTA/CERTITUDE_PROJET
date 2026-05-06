from django.urls import path, include
from .import views

app_name='courses'

urlpatterns = [
    path('list/', views.course_list_view , name='list')
]
