from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'level', 'price', 'start_date', 'end_date', 'is_active')
    list_filter   = ('level', 'is_active')
    search_fields = ('title', 'subjects')
    list_editable = ('is_active',)
    ordering      = ('level',)