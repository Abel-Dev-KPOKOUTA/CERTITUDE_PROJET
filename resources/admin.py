from django.contrib import admin
from django.utils.html import format_html
from .models import Subject, Level, Tip, Course

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'order', 'slug')
    list_editable = ('order',)

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'level', 'media_type', 'is_published', 'order')
    list_filter = ('subject', 'level', 'media_type', 'is_published')
    search_fields = ('title', 'tags')
    list_editable = ('order', 'is_published')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Identifiants', {'fields': ('title', 'slug', 'subject', 'level')}),
        ('Type et média', {'fields': ('media_type', 'media_file', 'video_url', 'thumbnail')}),
        ('Contenu', {'fields': ('summary', 'detailed_content')}),
        ('Téléchargement', {'fields': ('is_downloadable', 'download_file')}),
        ('Publication', {'fields': ('tags', 'order', 'is_published')}),
    )

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'level', 'nb_sheets', 'is_published', 'order')
    list_filter = ('subject', 'level', 'is_published')
    search_fields = ('title',)
    list_editable = ('order', 'is_published')
    prepopulated_fields = {'slug': ('title',)}