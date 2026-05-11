import uuid
from django.db import models
from enrollments.models import Enrollment


def generate_receipt_number():
    """Génère un numéro de reçu unique : LC-2026-XXXXXX"""
    return f"LC-2026-{uuid.uuid4().hex[:6].upper()}"


class Payment(models.Model):

    METHOD_CHOICES = [
        ('mtn',  'MTN Mobile Money'),
        ('moov', 'MOOV Money'),
    ]

    STATUS_CHOICES = [
        ('pending',   'En attente de confirmation'),
        ('confirmed', 'Confirmé'),
        ('failed',    'Rejeté'),
    ]

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Inscription"
    )

    # Montant et méthode
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Montant (FCFA)"
    )
    method = models.CharField(
        max_length=10, choices=METHOD_CHOICES,
        verbose_name="Réseau utilisé"
    )

    # Numéro utilisé par le payeur
    phone_used = models.CharField(
        max_length=20,
        verbose_name="Numéro ayant effectué le paiement"
    )

    # Statut
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name="Statut"
    )

    # Numéro de reçu unique
    receipt_number = models.CharField(
        max_length=30, unique=True,
        default=generate_receipt_number,
        verbose_name="Numéro de reçu"
    )

    # Dates
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name="Date de déclaration")
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de confirmation")
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Paiement"
        verbose_name_plural = "Paiements"
        ordering            = ['-created_at']

    def __str__(self):
        return (
            f"{self.receipt_number} — "
            f"{self.enrollment.full_name} — "
            f"{int(self.amount)} FCFA [{self.get_status_display()}]"
        )

    @property
    def destination_phone(self):
        return '01 96 38 92 49' if self.method == 'mtn' else '01 95 51 17 61'

    @property
    def destination_name(self):
        return 'CODJO Abel Jean Eudes'