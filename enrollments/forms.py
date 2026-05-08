from django import forms
from .models import Enrollment


class EnrollmentForm(forms.ModelForm):
    """
    Formulaire d'inscription unique.
    Le bloc parent s'affiche dynamiquement en JS si registrant_type == 'parent'.
    """

    class Meta:
        model  = Enrollment
        fields = [
            'registrant_type',
            'last_name', 'first_name', 'phone', 'school',
            'level', 'serie',
            'parent_name', 'parent_phone',
        ]
        widgets = {
            'registrant_type': forms.RadioSelect(),
            'last_name':  forms.TextInput(attrs={
                'placeholder': 'Ex : DOSSOU',
                'autocomplete': 'family-name',
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Ex : Koffi Emmanuel',
                'autocomplete': 'given-name',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Ex : 97 00 00 00',
                'type': 'tel',
                'autocomplete': 'tel',
            }),
            'school': forms.TextInput(attrs={
                'placeholder': 'Ex : CEG Zogbo',
            }),
            'level': forms.RadioSelect(),
            'serie': forms.RadioSelect(),
            'parent_name': forms.TextInput(attrs={
                'placeholder': 'Nom complet du parent / tuteur',
            }),
            'parent_phone': forms.TextInput(attrs={
                'placeholder': 'Ex : 96 00 00 00',
                'type': 'tel',
            }),
        }
        labels = {
            'registrant_type': "Qui effectue cette inscription ?",
            'last_name':       "Nom de l'élève",
            'first_name':      "Prénom(s) de l'élève",
            'phone':           "Téléphone de l'élève",
            'school':          "Établissement scolaire",
            'level':           "Niveau",
            'serie':           "Série",
            'parent_name':     "Nom du parent / tuteur",
            'parent_phone':    "Téléphone du parent",
        }

    def clean(self):
        cleaned = super().clean()
        rtype   = cleaned.get('registrant_type')

        # Si c'est un parent qui s'inscrit, le téléphone parent est obligatoire
        if rtype == 'parent':
            if not cleaned.get('parent_name'):
                self.add_error('parent_name', "Veuillez indiquer le nom du parent.")
            if not cleaned.get('parent_phone'):
                self.add_error('parent_phone', "Le téléphone du parent est obligatoire.")

        # Le niveau 3ème n'a pas de série → on force une valeur neutre
        level = cleaned.get('level')
        if level == '3eme':
            cleaned['serie'] = 'C'   # valeur par défaut, ignorée en affichage

        return cleaned