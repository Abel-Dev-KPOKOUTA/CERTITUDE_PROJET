from django.db import models
from enrollments.models import Enrollment


class Payment(models.Model):

    METHOD_CHOICES = [
        ('mtn',  'MTN Mobile Money'),
        ('moov', 'MOOV Money'),
    ]

    STATUS_CHOICES = [
        ('pending',   'En attente'),
        ('confirmed', 'Confirmé'),
        ('failed',    'Échoué'),
    ]

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Inscription"
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Montant (FCFA)"
    )
    method = models.CharField(
        max_length=10, choices=METHOD_CHOICES,
        blank=True, verbose_name="Réseau"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name="Statut"
    )

    # FeexPay
    feexpay_reference = models.CharField(
        max_length=200, blank=True,
        verbose_name="Référence FeexPay"
    )
    phone_used = models.CharField(
        max_length=20, blank=True,
        verbose_name="Numéro utilisé pour le paiement"
    )

    paid_at    = models.DateTimeField(null=True, blank=True, verbose_name="Payé le")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Paiement"
        verbose_name_plural = "Paiements"
        ordering            = ['-created_at']

    def __str__(self):
        return (
            f"{self.enrollment.full_name} — "
            f"{int(self.amount)} FCFA [{self.get_status_display()}]"
        )