from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Level(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tip(models.Model):
    MEDIA_TYPES = [
        ('text', 'Texte structuré'),
        ('image', 'Image'),
        ('video', 'Vidéo'),
        ('pdf', 'PDF'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tips')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='tips')
    
    # Type de contenu
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='text')
    
    # Fichier ou URL selon le type
    media_file = models.FileField(
        upload_to='tips/media/', blank=True, null=True,
        help_text="Image, PDF ou vidéo (si fichier local)"
    )
    video_url = models.URLField(blank=True, help_text="URL YouTube/Viméo (si vidéo hébergée)")
    thumbnail = models.ImageField(upload_to='tips/thumbnails/', blank=True, null=True)
    
    # Texte court pour la carte
    summary = models.CharField(max_length=200, blank=True)
    
    # Contenu détaillé (explications, description de l'image, etc.)
    detailed_content = models.TextField(blank=True, help_text="Description ou contenu textuel de l'astuce")
    
    # Téléchargement
    is_downloadable = models.BooleanField(default=False)
    download_file = models.FileField(upload_to='tips/downloads/', blank=True, null=True)
    
    # Métadonnées
    tags = models.CharField(max_length=500, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Tip.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('resources:tip_detail', args=[self.slug])

    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='courses')
    
    # Affichage sur la carte
    badge_text = models.CharField(max_length=100, blank=True)
    short_description = models.TextField(max_length=500)
    
    # Contenu détaillé (page du cours)
    detailed_description = models.TextField(blank=True, help_text="Contenu complet du cours (HTML accepté)")
    
    # Métadonnées
    sub_subjects = models.JSONField(default=list, blank=True)
    nb_sheets = models.PositiveSmallIntegerField(default=0)
    nb_exercises = models.PositiveSmallIntegerField(default=0)
    has_corrections = models.BooleanField(default=True)
    has_audio = models.BooleanField(default=False)
    
    # Fichier PDF principal
    pdf_file = models.FileField(upload_to='courses/pdfs/', blank=True, null=True)
    
    # Aperçu (image ou texte)
    preview_image = models.ImageField(upload_to='courses/previews/', blank=True, null=True)
    preview_text = models.TextField(blank=True, help_text="Extrait pour aperçu popup")
    
    # Téléchargement
    is_downloadable = models.BooleanField(default=True)
    
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'level__order', 'subject__name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Course.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('resources:course_detail', args=[self.slug])

    def __str__(self):
        return f"{self.title} - {self.level.name}"