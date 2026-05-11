from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('receipt_number', 'student_name', 'level_info', 'amount_display', 'method_display', 'phone_used', 'status_badge', 'created_at')
    list_filter   = ('status', 'method', 'created_at')
    search_fields = ('receipt_number', 'enrollment__last_name', 'enrollment__first_name', 'phone_used')
    ordering      = ('-created_at',)
    readonly_fields = ('receipt_number', 'created_at', 'updated_at', 'confirmed_at', 'phone_used', 'method')

    fieldsets = (
        ("🧾 Reçu",        { 'fields': ('receipt_number', 'created_at') }),
        ("👤 Inscription", { 'fields': ('enrollment',) }),
        ("💳 Paiement",    { 'fields': ('amount', 'method', 'phone_used', 'status', 'confirmed_at') }),
        ("📅 Dates",       { 'fields': ('updated_at',), 'classes': ('collapse',) }),
    )

    def student_name(self, obj):
        return obj.enrollment.full_name
    student_name.short_description = 'Élève'

    def level_info(self, obj):
        return obj.enrollment.level_serie
    level_info.short_description = 'Formation'

    def amount_display(self, obj):
        return format_html('<strong>{} FCFA</strong>', f"{int(obj.amount):,}".replace(',', ' '))
    amount_display.short_description = 'Montant'

    def method_display(self, obj):
        icons = {'mtn': '🟡 MTN', 'moov': '🔵 MOOV'}
        return icons.get(obj.method, '—')
    method_display.short_description = 'Réseau'

    def status_badge(self, obj):
        styles = {
            'pending':   ('⏳', '#f59e0b', '#fff7ed', 'En attente'),
            'confirmed': ('✅', '#10b981', '#d1fae5', 'Confirmé'),
            'failed':    ('❌', '#ef4444', '#fef2f2', 'Rejeté'),
        }
        icon, color, bg, label = styles.get(obj.status, ('', '#999', '#eee', obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700">{} {}</span>',
            bg, color, icon, label
        )
    status_badge.short_description = 'Statut'

    actions = ['confirm_payments', 'reject_payments']

    def confirm_payments(self, request, queryset):
        updated = 0
        for payment in queryset.filter(status='pending'):
            payment.status       = 'confirmed'
            payment.confirmed_at = timezone.now()
            payment.save()
            payment.enrollment.activate_if_paid()
            updated += 1
        self.message_user(request, f"✅ {updated} paiement(s) confirmé(s). Les inscriptions sont activées.")
    confirm_payments.short_description = "✅ Confirmer les paiements sélectionnés"

    def reject_payments(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"❌ {queryset.count()} paiement(s) rejeté(s).")
    reject_payments.short_description = "❌ Rejeter les paiements sélectionnés"