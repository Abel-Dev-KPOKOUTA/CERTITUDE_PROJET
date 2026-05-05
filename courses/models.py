from django.db import models


class Course(models.Model):

    LEVEL_CHOICES = [
        ('3eme',  '3ème'),
        ('1ereC', '1ère C'),
        ('1ereD', '1ère D'),
        ('tleC',  'Terminale C'),
        ('tleD',  'Terminale D'),
    ]

    title       = models.CharField(max_length=200, verbose_name="Titre")
    level       = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name="Classe")
    description = models.TextField(blank=True, verbose_name="Description")
    subjects    = models.CharField(max_length=300, verbose_name="Matières enseignées",
                                   help_text="Ex : Maths, PCT, SVT, Anglais")
    price       = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Tarif (FCFA)")
    start_date  = models.DateField(verbose_name="Date de début")
    end_date    = models.DateField(verbose_name="Date de fin")
    is_active   = models.BooleanField(default=True, verbose_name="Disponible")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Formation"
        verbose_name_plural = "Formations"
        ordering            = ['level']

    def __str__(self):
        return f"{self.get_level_display()} — {self.title}"

    @property
    def first_tranche(self):
        """50% du prix arrondi."""
        return int(self.price * 50 / 100)

    @property
    def second_tranche(self):
        """Reste après la première tranche."""
        return int(self.price) - self.first_tranche