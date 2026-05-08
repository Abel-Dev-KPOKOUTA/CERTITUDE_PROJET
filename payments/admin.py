from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('student_name', 'amount_display', 'method_display', 'status_badge', 'fedapay_transaction_id', 'paid_at', 'created_at')
    list_filter   = ('status', 'method', 'created_at')
    search_fields = ('enrollment__last_name', 'enrollment__first_name', 'enrollment__phone', 'fedapay_transaction_id')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'paid_at', 'fedapay_transaction_id', 'fedapay_token')

    fieldsets = (
        ("👤 Inscription", {
            'fields': ('enrollment',),
        }),
        ("💳 Paiement", {
            'fields': ('amount', 'method', 'status', 'paid_at'),
        }),
        ("🔗 FedaPay", {
            'fields': ('fedapay_transaction_id', 'fedapay_token'),
            'classes': ('collapse',),
        }),
        ("📅 Dates", {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def student_name(self, obj):
        return obj.enrollment.full_name
    student_name.short_description = 'Élève'

    def amount_display(self, obj):
        return format_html('<strong>{} FCFA</strong>', f"{int(obj.amount):,}".replace(',', ' '))
    amount_display.short_description = 'Montant'

    def method_display(self, obj):
        icons = {'mtn': '📱 MTN MoMo', 'moov': '📱 MOOV Money', 'cash': '💵 Espèces'}
        return icons.get(obj.method, obj.method or '—')
    method_display.short_description = 'Méthode'

    def status_badge(self, obj):
        styles = {
            'pending':   ('🟡', '#f59e0b', '#fff7ed', 'En attente'),
            'confirmed': ('✅', '#10b981', '#d1fae5', 'Confirmé'),
            'failed':    ('❌', '#ef4444', '#fef2f2', 'Échoué'),
        }
        icon, color, bg, label = styles.get(obj.status, ('', '#999', '#eee', obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700">{} {}</span>',
            bg, color, icon, label
        )
    status_badge.short_description = 'Statut'

    actions = ['confirm_payments']

    def confirm_payments(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for payment in queryset.filter(status='pending'):
            payment.status  = 'confirmed'
            payment.paid_at = timezone.now()
            payment.save()
            payment.enrollment.activate_if_paid()
            updated += 1
        self.message_user(request, f"{updated} paiement(s) confirmé(s) et inscription(s) activée(s).")
    confirm_payments.short_description = "✅ Confirmer les paiements sélectionnés"