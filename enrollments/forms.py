from django import forms
from .models import Enrollment


class EnrollmentForm(forms.ModelForm):

    class Meta:
        model  = Enrollment
        fields = [
            'registrant_type',
            'last_name', 'first_name', 'school',
            'phone', 'phone_owner',
            'level', 'serie',
            'parent_name', 'parent_phone',
        ]
        widgets = {
            'registrant_type': forms.RadioSelect(),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Ex : DOSSOU'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Ex : Koffi Emmanuel'}),
            'school':     forms.TextInput(attrs={'placeholder': 'Ex : CEG Zogbo'}),
            'phone':      forms.TextInput(attrs={
                'placeholder': 'Ex : 97 00 00 00',
                'type': 'tel',
            }),
            'phone_owner':  forms.RadioSelect(),
            'level':        forms.RadioSelect(),
            'serie':        forms.RadioSelect(),
            'parent_name':  forms.TextInput(attrs={'placeholder': 'Nom complet du parent / tuteur'}),
            'parent_phone': forms.TextInput(attrs={
                'placeholder': 'Ex : 96 00 00 00',
                'type': 'tel',
            }),
        }
        labels = {
            'registrant_type': "Qui effectue cette inscription ?",
            'last_name':       "Nom de l'élève",
            'first_name':      "Prénom(s) de l'élève",
            'school':          "Établissement scolaire",
            'phone':           "Numéro de contact",
            'phone_owner':     "Ce numéro appartient à",
            'level':           "Niveau",
            'serie':           "Série",
            'parent_name':     "Nom du parent / tuteur",
            'parent_phone':    "Téléphone du parent",
        }

    def clean(self):
        cleaned = super().clean()
        rtype   = cleaned.get('registrant_type')

        if rtype == 'parent':
            if not cleaned.get('parent_name'):
                self.add_error('parent_name', "Veuillez indiquer le nom du parent.")
            if not cleaned.get('parent_phone'):
                self.add_error('parent_phone', "Le téléphone du parent est obligatoire.")

        # 3ème → pas de série
        if cleaned.get('level') == '3eme':
            cleaned['serie'] = 'C'

        return cleaned