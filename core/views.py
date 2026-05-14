import os
from django.conf import settings
from django.shortcuts import render


def home(request):
    return render(request, 'core/index.html')

def galerie(request):
    """
    Scanne le dossier static/images/ et catégorise automatiquement selon le nom :
    - groupe*.jpg  → catégorie "groupe"
    - prix*.jpg    → catégorie "prix"
    - autres       → catégorie "cours"
    """
    # Changez ici : utilisez STATIC_ROOT au lieu de MEDIA_ROOT
    images_dir = os.path.join(settings.STATIC_ROOT, 'images')
    
    # Si STATIC_ROOT n'existe pas, utilisez STATICFILES_DIRS
    if not os.path.exists(images_dir):
        images_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
    
    images = []

    EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG')

    if os.path.exists(images_dir):
        fichiers = sorted(os.listdir(images_dir))

        for filename in fichiers:
            # Ignorer tout ce qui n'est pas une image
            if not filename.endswith(EXTENSIONS):
                continue
            # Ignorer le logo
            if 'logo' in filename.lower():
                continue
            if 'affiche' in filename.lower():
                continue

            name_lower = filename.lower()

            # Détection de catégorie par préfixe
            if name_lower.startswith('groupe'):
                category       = 'groupe'
                category_label = 'Photo de famille'
            elif name_lower.startswith('prix'):
                category       = 'prix'
                category_label = 'Remise de prix'
            else:
                category       = 'cours'
                category_label = 'Cours'

            # Utilisez STATIC_URL pour le chemin
            images.append({
                'src':      f'{settings.STATIC_URL}images/{filename}',  # Changé ici
                'alt':      f'Édition 2025 — {filename.replace(".jpg", "").replace(".png", "").replace(".JPG", "")}',
                'category': category,
                'label':    category_label,
            })

    # Compter par catégorie pour les filtres
    counts = {
        'all':    len(images),
        'cours':  sum(1 for i in images if i['category'] == 'cours'),
        'groupe': sum(1 for i in images if i['category'] == 'groupe'),
        'prix':   sum(1 for i in images if i['category'] == 'prix'),
    }

    return render(request, 'core/galerie.html', {
        'images': images,
        'counts': counts,
    })

def temoignages(request):
    """
    Liste des vidéos de témoignages.
    Remplace les youtube_id par les vrais IDs après upload sur YouTube.
    """
    videos = [
        {
            'youtube_id': 'VOTRE_ID_1',
            'nom':    'Koffi Emmanuel',
            'niveau': '1ère C',
            'ecole':  'CEG Zogbo',
            'quote':  "Grâce à La Certitude, j'ai tout compris en 2 mois !",
        },
        {
            'youtube_id': 'VOTRE_ID_2',
            'nom':    'Adjoua Marie',
            'niveau': 'Terminale D',
            'ecole':  'Lycée Béhanzin',
            'quote':  "Les profs sont très pédagogues et disponibles.",
        },
        {
            'youtube_id': 'VOTRE_ID_3',
            'nom':    'Rodrigue Hounkpe',
            'niveau': '3ème',
            'ecole':  'CEG Gbégamey',
            'quote':  "J'ai validé mon BEPC grâce à ce renforcement.",
        },
        {
            'youtube_id': 'VOTRE_ID_4',
            'nom':    'Fatouma Seidou',
            'niveau': '1ère D',
            'ecole':  'CEG Sainte Rita',
            'quote':  "Une ambiance studieuse et motivante.",
        },
        {
            'youtube_id': 'VOTRE_ID_5',
            'nom':    'Parent de Brice',
            'niveau': 'Terminale C',
            'ecole':  'Lycée Coulibaly',
            'quote':  "Mon fils a énormément progressé. Je recommande.",
        },
        {
            'youtube_id': 'VOTRE_ID_6',
            'nom':    'Aïssatou Diallo',
            'niveau': '3ème',
            'ecole':  'CEG Fidjrossè',
            'quote':  "Le meilleur investissement pour les vacances.",
        },
        {
            'youtube_id': 'VOTRE_ID_7',
            'nom':    'Wilfried Dossou',
            'niveau': '1ère C',
            'ecole':  'Collège Baptiste',
            'quote':  "Programme complet, professeurs expérimentés.",
        },
        {
            'youtube_id': 'VOTRE_ID_8',
            'nom':    'Parent de Sonia',
            'niveau': 'Terminale D',
            'ecole':  'Lycée Mathieu Bouké',
            'quote':  "Ma fille a eu son BAC. Merci La Certitude !",
        },
        {
            'youtube_id': 'VOTRE_ID_9',
            'nom':    'Cédric Agossou',
            'niveau': '1ère D',
            'ecole':  'CEG Zogbo',
            'quote':  "Des cours bien organisés et très efficaces.",
        },
        {
            'youtube_id': 'VOTRE_ID_10',
            'nom':    'Aline Tchokpon',
            'niveau': '3ème',
            'ecole':  'CEG Gbégamey Sud',
            'quote':  "Je reviendrai l'année prochaine sans hésiter.",
        },
    ]

    return render(request, 'core/temoignages.html', {'videos': videos})

def astuces(request):
    pass
