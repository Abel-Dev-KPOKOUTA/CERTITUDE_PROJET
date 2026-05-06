from django.contrib import admin
from django.utils.html import format_html
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('who_display', 'course', 'status_badge', 'total_paid_display', 'created_at')
    list_filter   = ('status', 'course__level', 'created_at')
    search_fields = ('student__last_name', 'student__first_name', 'course__title')
    ordering      = ('-created_at',)
    actions       = ['activate_enrollments', 'cancel_enrollments']

    def who_display(self, obj):
        return obj.who
    who_display.short_description = 'Apprenant'

    def status_badge(self, obj):
        colors = {
            'pending':   ('#c9922a', 'En attente'),
            'active':    ('#2a7f6f', 'Active'),
            'cancelled': ('#e53e3e', 'Annulée'),
        }
        color, label = colors.get(obj.status, ('#999', obj.status))
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">{}</span>',
            color, label
        )
    status_badge.short_description = 'Statut'

    def total_paid_display(self, obj):
        return f"{int(obj.total_paid):,} / {int(obj.course.price):,} FCFA".replace(',', ' ')
    total_paid_display.short_description = 'Paiement'

    def activate_enrollments(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} inscription(s) activée(s).")
    activate_enrollments.short_description = "✅ Activer les inscriptions"

    def cancel_enrollments(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} inscription(s) annulée(s).")
    cancel_enrollments.short_description = "❌ Annuler les inscriptions"