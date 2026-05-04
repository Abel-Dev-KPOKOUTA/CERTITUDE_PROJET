from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Student


# ─────────────────────────────────────────────────────────
#  USER ADMIN
# ─────────────────────────────────────────────────────────
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'full_name', 'role_badge', 'phone', 'level_or_matiere', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_active', 'level', 'matiere')
    search_fields = ('username', 'first_name', 'last_name', 'phone', 'school')
    ordering      = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations complémentaires', {
            'fields': ('role', 'phone', 'photo'),
        }),
        ('Apprenant', {
            'fields': ('school', 'level'),
            'classes': ('collapse',),
        }),
        ('Professeur', {
            'fields': ('matiere', 'bio'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Rôle & infos', {
            'fields': ('role', 'first_name', 'last_name', 'phone', 'school', 'level', 'matiere'),
        }),
    )

    def role_badge(self, obj):
        colors = {
            'apprenant': '#2a7f6f',
            'parent':    '#c9922a',
            'prof':      '#0b1c3d',
            'admin':     '#e53e3e',
        }
        color = colors.get(obj.role, '#999')
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Rôle'

    def level_or_matiere(self, obj):
        if obj.role == 'apprenant' and obj.level:
            return obj.get_level_display()
        if obj.role == 'prof' and obj.matiere:
            return obj.get_matiere_display()
        return '—'
    level_or_matiere.short_description = 'Niveau / Matière'

    # Action : créer un compte apprenant depuis une fiche Student
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} compte(s) activé(s).")
    activate_users.short_description = "Activer les comptes sélectionnés"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} compte(s) désactivé(s).")
    deactivate_users.short_description = "Désactiver les comptes sélectionnés"


# ─────────────────────────────────────────────────────────
#  STUDENT ADMIN
# ─────────────────────────────────────────────────────────
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'level_display', 'school', 'parent_name', 'has_account', 'created_at')
    list_filter   = ('level', 'created_at')
    search_fields = ('last_name', 'first_name', 'school', 'parent__last_name', 'parent__first_name')
    ordering      = ('last_name', 'first_name')
    raw_id_fields = ('parent', 'user_account')

    def level_display(self, obj):
        return obj.get_level_display()
    level_display.short_description = 'Niveau'

    def parent_name(self, obj):
        return obj.parent.full_name
    parent_name.short_description = 'Parent / Tuteur'

    def has_account(self, obj):
        if obj.user_account:
            return format_html('<span style="color:#2a7f6f;font-weight:700">✓ Oui</span>')
        return format_html('<span style="color:#e53e3e">✗ Non</span>')
    has_account.short_description = 'Compte plateforme'