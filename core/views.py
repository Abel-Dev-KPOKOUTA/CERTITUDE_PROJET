from django.shortcuts import render


def home(request):
    return render(request, 'core/index.html')


def galerie(request):
    # Génère dynamiquement les 50 images
    images = [
        {'src': f'/images/{i}.jpg', 'alt': f'Édition 2025 — photo {i}'}
        for i in range(1, 51)
    ]
    return render(request, 'core/galerie.html', {'images': images})


def temoignages(request):
    # Remplace les youtube_id par les vrais IDs après upload
    videos = [
        {'youtube_id': 'VOTRE_ID_1',  'nom': 'Koffi Emmanuel',   'niveau': '1ère C',        'ecole': 'CEG Zogbo'},
        {'youtube_id': 'VOTRE_ID_2',  'nom': 'Adjoua Marie',     'niveau': 'Terminale D',   'ecole': 'Lycée Béhanzin'},
        {'youtube_id': 'VOTRE_ID_3',  'nom': 'Rodrigue Hounkpe', 'niveau': '3ème',          'ecole': 'CEG Gbégamey'},
        {'youtube_id': 'VOTRE_ID_4',  'nom': 'Fatouma Seidou',   'niveau': '1ère D',        'ecole': 'CEG Sainte Rita'},
        {'youtube_id': 'VOTRE_ID_5',  'nom': 'Parent de Brice',  'niveau': 'Terminale C',   'ecole': 'Lycée Coulibaly'},
        {'youtube_id': 'VOTRE_ID_6',  'nom': 'Aïssatou Diallo',  'niveau': '3ème',          'ecole': 'CEG Fidjrossè'},
        {'youtube_id': 'VOTRE_ID_7',  'nom': 'Wilfried Dossou',  'niveau': '1ère C',        'ecole': 'Collège Baptiste'},
        {'youtube_id': 'VOTRE_ID_8',  'nom': 'Parent de Sonia',  'niveau': 'Terminale D',   'ecole': 'Lycée Mathieu Bouké'},
        {'youtube_id': 'VOTRE_ID_9',  'nom': 'Cédric Agossou',   'niveau': '1ère D',        'ecole': 'CEG Zogbo'},
        {'youtube_id': 'VOTRE_ID_10', 'nom': 'Aline Tchokpon',   'niveau': '3ème',          'ecole': 'CEG Gbégamey Sud'},
    ]
    return render(request, 'core/temoignages.html', {'videos': videos})