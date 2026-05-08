from django.contrib import admin
from django.utils.html import format_html
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'level_serie_display', 'phone', 'school', 'status_badge', 'created_at')
    list_filter   = ('status', 'level', 'serie', 'registrant_type')
    search_fields = ('last_name', 'first_name', 'phone', 'school', 'parent_name', 'parent_phone')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("👤 Élève", {
            'fields': ('registrant_type', 'last_name', 'first_name', 'phone', 'school'),
        }),
        ("📚 Formation", {
            'fields': ('level', 'serie'),
        }),
        ("👨‍👩‍👦 Parent / Tuteur", {
            'fields': ('parent_name', 'parent_phone'),
            'classes': ('collapse',),
        }),
        ("📊 Statut", {
            'fields': ('status', 'created_at', 'updated_at'),
        }),
    )

    def level_serie_display(self, obj):
        if obj.level == '3eme':
            return obj.get_level_display()
        return f"{obj.get_level_display()} — Série {obj.serie}"
    level_serie_display.short_description = 'Niveau / Série'

    def status_badge(self, obj):
        colors = {
            'pending':   ('#f59e0b', '#fff7ed', 'En attente'),
            'active':    ('#10b981', '#d1fae5', 'Inscrit ✓'),
            'cancelled': ('#ef4444', '#fef2f2', 'Annulé'),
        }
        color, bg, label = colors.get(obj.status, ('#999', '#eee', obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">{}</span>',
            bg, color, label
        )
    status_badge.short_description = 'Statut'

    actions = ['mark_active', 'mark_cancelled']

    def mark_active(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} inscription(s) activée(s).")
    mark_active.short_description = "✅ Marquer comme inscrit"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} inscription(s) annulée(s).")
    mark_cancelled.short_description = "❌ Annuler les inscriptions"