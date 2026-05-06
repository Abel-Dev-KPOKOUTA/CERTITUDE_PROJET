from django.db import models


class Payment(models.Model):

    METHOD_CHOICES = [
        ('mtn',   'MTN Mobile Money'),
        ('moov',  'MOOV Money'),
        ('celtiis', 'Celtiis Money'),
        ('cash',  'Espèces sur place'),
    ]

    STATUS_CHOICES = [
        ('pending',   'En attente'),
        ('confirmed', 'Confirmé'),
        ('failed',    'Échoué'),
    ]

    enrollment = models.ForeignKey(
        'enrollments.Enrollment',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Inscription",
    )
    amount     = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Montant (FCFA)")
    method     = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name="Méthode")
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    reference  = models.CharField(max_length=100, blank=True, verbose_name="Référence transaction")
    paid_at    = models.DateTimeField(null=True, blank=True, verbose_name="Payé le")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Paiement"
        verbose_name_plural = "Paiements"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.enrollment} — {self.amount} FCFA ({self.get_status_display()})"