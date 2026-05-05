from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Utilisateur unique avec rôle explicite.
    Rôles : apprenant | parent | prof | admin
    """

    ROLE_CHOICES = [
        ('apprenant', 'Apprenant'),
        ('parent',    'Parent / Tuteur'),
        ('prof',      'Professeur'),
        ('admin',     'Administrateur'),
    ]

    LEVEL_CHOICES = [
        ('3eme',  '3ème'),
        ('1ereC', '1ère C'),
        ('1ereD', '1ère D'),
        ('tleC',  'Terminale C'),
        ('tleD',  'Terminale D'),
    ]

    MATIERE_CHOICES = [
        ('maths',   'Mathématiques'),
        ('pct',     'PCT'),
        ('svt',     'SVT'),
        ('anglais', 'Anglais'),
    ]

    # ── Commun à tous ───────────────────────────────────────
    role    = models.CharField(max_length=20, choices=ROLE_CHOICES, default='apprenant', verbose_name="Rôle")
    phone   = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    photo   = models.ImageField(upload_to='photos/', blank=True, null=True, verbose_name="Photo de profil")

    # ── Apprenant ───────────────────────────────────────────
    school  = models.CharField(max_length=200, blank=True, verbose_name="Établissement scolaire")
    level   = models.CharField(max_length=10, choices=LEVEL_CHOICES, blank=True, verbose_name="Classe / Niveau")

    # ── Prof ────────────────────────────────────────────────
    matiere = models.CharField(max_length=20, choices=MATIERE_CHOICES, blank=True, verbose_name="Matière enseignée")
    bio     = models.TextField(blank=True, verbose_name="Présentation")

    class Meta:
        verbose_name        = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering            = ['-date_joined']

    def __str__(self):
        return f"[{self.get_role_display()}] {self.last_name} {self.first_name}"

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.username

    # ── Raccourcis rôle ─────────────────────────────────────
    @property
    def is_apprenant(self):
        return self.role == 'apprenant'

    @property
    def is_parent_role(self):
        return self.role == 'parent'

    @property
    def is_prof(self):
        return self.role == 'prof'

    @property
    def is_admin_role(self):
        return self.role == 'admin'


class Student(models.Model):
    """
    Fiche enfant rattachée à un compte parent.
    Le compte User apprenant est optionnel — créé par l'admin si besoin.
    """

    LEVEL_CHOICES = [
        ('3eme',  '3ème'),
        ('1ereC', '1ère C'),
        ('1ereD', '1ère D'),
        ('tleC',  'Terminale C'),
        ('tleD',  'Terminale D'),
    ]

    # Lien vers le parent
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='children',
        limit_choices_to={'role': 'parent'},
        verbose_name="Parent / Tuteur",
    )

    # Compte apprenant optionnel (créé par l'admin après)
    user_account = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='student_profile',
        limit_choices_to={'role': 'apprenant'},
        verbose_name="Compte apprenant (créé par l'admin)",
    )

    # Infos de l'enfant
    last_name  = models.CharField(max_length=100, verbose_name="Nom")
    first_name = models.CharField(max_length=100, verbose_name="Prénom(s)")
    school     = models.CharField(max_length=200, verbose_name="Établissement scolaire")
    level      = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name="Classe / Niveau")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Fiche apprenant"
        verbose_name_plural = "Fiches apprenants"
        ordering            = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} — {self.get_level_display()} (parent : {self.parent.full_name})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"