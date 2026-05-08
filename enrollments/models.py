from django.db import models


class Enrollment(models.Model):
    """
    Inscription d'un élève aux cours de renforcement.
    Pas de compte utilisateur requis — juste les infos essentielles.
    """

    TYPE_CHOICES = [
        ('eleve',  'L\'élève lui-même'),
        ('parent', 'Un parent / tuteur'),
    ]

    LEVEL_CHOICES = [
        ('3eme', '3ème'),
        ('1ere', '1ères C & D'),
        ('tle',  'Terminales C & D'),
    ]

    SERIE_CHOICES = [
        ('C', 'Série C'),
        ('D', 'Série D'),
    ]

    STATUS_CHOICES = [
        ('pending',   'En attente de paiement'),
        ('active',    'Inscrit — Paiement confirmé'),
        ('cancelled', 'Annulé'),
    ]

    # ── Qui s'inscrit ───────────────────────────────────────
    registrant_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='eleve',
        verbose_name="Qui s'inscrit"
    )

    # ── Informations de l'élève ─────────────────────────────
    last_name  = models.CharField(max_length=100, verbose_name="Nom de l'élève")
    first_name = models.CharField(max_length=100, verbose_name="Prénom(s) de l'élève")
    phone      = models.CharField(max_length=20,  verbose_name="Téléphone de l'élève")
    school     = models.CharField(max_length=200, verbose_name="Établissement scolaire")

    # ── Niveau & Série ──────────────────────────────────────
    level = models.CharField(
        max_length=10, choices=LEVEL_CHOICES,
        verbose_name="Niveau"
    )
    serie = models.CharField(
        max_length=1, choices=SERIE_CHOICES,
        verbose_name="Série"
    )

    # ── Informations du parent (optionnel) ──────────────────
    parent_name  = models.CharField(max_length=200, blank=True, verbose_name="Nom du parent / tuteur")
    parent_phone = models.CharField(max_length=20,  blank=True, verbose_name="Téléphone du parent")

    # ── Statut & Dates ──────────────────────────────────────
    status     = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.get_level_display()} {self.serie} [{self.get_status_display()}]"

    # ── Propriétés utiles ───────────────────────────────────
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def level_serie(self):
        """Ex : '1ère C', 'Terminale D', '3ème' """
        label = self.get_level_display()
        if self.level == '3eme':
            return label
        return f"{label} — Série {self.serie}"

    @property
    def contact_phone(self):
        """Numéro prioritaire pour les SMS : parent si existe, sinon élève."""
        return self.parent_phone if self.parent_phone else self.phone

    @property
    def tarif(self):
        tarifs = {'3eme': 11500, '1ere': 12500, 'tle': 15500}
        return tarifs.get(self.level, 0)

    @property
    def is_paid(self):
        """True si au moins un paiement confirmé couvre le tarif total."""
        try:
            from django.db.models import Sum
            total = self.payments.filter(status='confirmed').aggregate(
                total=Sum('amount')
            )['total'] or 0
            return total >= self.tarif
        except Exception:
            return False

    def activate_if_paid(self):
        """Active l'inscription si le paiement est complet."""
        if self.is_paid and self.status == 'pending':
            self.status = 'active'
            self.save(update_fields=['status'])
            return True
        return False