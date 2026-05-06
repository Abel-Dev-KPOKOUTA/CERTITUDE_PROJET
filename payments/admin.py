from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('enrollment', 'amount_display', 'method', 'status_badge', 'created_at')
    list_filter   = ('status', 'method', 'created_at')
    search_fields = ('enrollment__student__last_name', 'enrollment__student__first_name', 'reference')
    ordering      = ('-created_at',)
    actions       = ['confirm_payments']

    def amount_display(self, obj):
        return f"{int(obj.amount):,} FCFA".replace(',', ' ')
    amount_display.short_description = 'Montant'

    def status_badge(self, obj):
        colors = {
            'pending':   ('#c9922a', 'En attente'),
            'confirmed': ('#2a7f6f', 'Confirmé'),
            'failed':    ('#e53e3e', 'Échoué'),
        }
        color, label = colors.get(obj.status, ('#999', obj.status))
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700">{}</span>',
            color, label
        )
    status_badge.short_description = 'Statut'

    def confirm_payments(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for payment in queryset.filter(status='pending'):
            payment.status  = 'confirmed'
            payment.paid_at = timezone.now()
            payment.save()
            # Activer l'inscription si paiement complet
            enrollment = payment.enrollment
            if enrollment.is_fully_paid:
                enrollment.status = 'active'
                enrollment.save()
            updated += 1
        self.message_user(request, f"{updated} paiement(s) confirmé(s).")
    confirm_payments.short_description = "✅ Confirmer les paiements sélectionnés"