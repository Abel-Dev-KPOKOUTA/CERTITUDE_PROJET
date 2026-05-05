from django.db import models
from django.conf import settings


class Enrollment(models.Model):

    STATUS_CHOICES = [
        ('pending',   'En attente de paiement'),
        ('active',    'Active'),
        ('cancelled', 'Annulée'),
    ]

    # L'apprenant (compte User direct)
    student    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'apprenant'},
        null=True, blank=True,
        verbose_name="Apprenant (compte)",
    )

    # OU l'enfant (fiche Student liée à un parent)
    student_child = models.ForeignKey(
        'users.Student',
        on_delete=models.CASCADE,
        related_name='enrollments',
        null=True, blank=True,
        verbose_name="Apprenant (enfant de parent)",
    )

    course     = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Formation",
    )
    status     = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering            = ['-created_at']
        # Un apprenant ne peut s'inscrire qu'une fois par cours
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                condition=models.Q(student__isnull=False),
                name='unique_student_course',
            ),
            models.UniqueConstraint(
                fields=['student_child', 'course'],
                condition=models.Q(student_child__isnull=False),
                name='unique_child_course',
            ),
        ]

    def __str__(self):
        who = self.student or self.student_child
        return f"{who} → {self.course}"

    @property
    def who(self):
        """Retourne l'apprenant (User ou Student)."""
        return self.student or self.student_child

    @property
    def total_paid(self):
        """Somme des paiements confirmés."""
        return self.payments.filter(
            status='confirmed'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def remaining(self):
        """Montant restant à payer."""
        return int(self.course.price) - int(self.total_paid)

    @property
    def is_fully_paid(self):
        return self.remaining <= 0

    @property
    def payment_percent(self):
        if not self.course.price:
            return 0
        return min(int(self.total_paid * 100 / self.course.price), 100)