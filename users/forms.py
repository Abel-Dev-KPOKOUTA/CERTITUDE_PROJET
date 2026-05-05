import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()


# ─────────────────────────────────────────────────────────
#  VALIDATION MOT DE PASSE — règles communes
# ─────────────────────────────────────────────────────────
def validate_password_strength(password):
    """
    Règles :
      - 8 caractères minimum
      - Au moins 1 majuscule
      - Au moins 1 chiffre
      - Au moins 1 caractère spécial
    """
    if not password:
        return
    errors = []
    if len(password) < 8:
        errors.append("au moins 8 caractères")
    if not re.search(r'[A-Z]', password):
        errors.append("au moins une lettre majuscule (A-Z)")
    if not re.search(r'[0-9]', password):
        errors.append("au moins un chiffre (0-9)")
    if not re.search(r'[!@#$%^&*()_\-+=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append("au moins un caractère spécial (!@#$%...)")
    if errors:
        raise forms.ValidationError(
            "Mot de passe trop faible. Il doit contenir : " + ", ".join(errors) + "."
        )


# ─────────────────────────────────────────────────────────
#  INSCRIPTION APPRENANT
# ─────────────────────────────────────────────────────────
class ApprenantRegisterForm(forms.ModelForm):
    """Inscription directe d'un apprenant."""

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ex : MonPass@2026',
            'id': 'id_password1',
        }),
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Répétez le mot de passe',
            'id': 'id_password2',
        }),
    )

    class Meta:
        model  = User
        fields = ['last_name', 'first_name', 'phone', 'school', 'level', 'email', 'username']
        widgets = {
            'last_name':  forms.TextInput(attrs={'placeholder': 'Ex : DOSSOU'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Ex : Koffi Emmanuel'}),
            'phone':      forms.TextInput(attrs={'placeholder': 'Ex : 97000000', 'type': 'tel'}),
            'school':     forms.TextInput(attrs={'placeholder': 'Ex : CEG Zogbo'}),
            'level':      forms.Select(),
            'email':      forms.EmailInput(attrs={'placeholder': 'exemple@mail.com (optionnel)'}),
            'username':   forms.TextInput(attrs={'placeholder': "Ex : koffi2026"}),
        }
        labels = {
            'last_name':  'Nom',
            'first_name': 'Prénom(s)',
            'phone':      'Téléphone',
            'school':     'Établissement scolaire',
            'level':      'Classe / Niveau',
            'email':      'Email (optionnel)',
            'username':   "Nom d'utilisateur",
        }

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password_strength(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Les mots de passe ne correspondent pas.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'apprenant'
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────────────────
#  INSCRIPTION PARENT
# ─────────────────────────────────────────────────────────
class ParentRegisterForm(forms.ModelForm):
    """Inscription d'un parent / tuteur."""

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ex : MonPass@2026',
            'id': 'id_password1',
        }),
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Répétez le mot de passe',
            'id': 'id_password2',
        }),
    )

    class Meta:
        model  = User
        fields = ['last_name', 'first_name', 'phone', 'email', 'username']
        widgets = {
            'last_name':  forms.TextInput(attrs={'placeholder': 'Ex : DOSSOU'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Ex : Adjoua Marie'}),
            'phone':      forms.TextInput(attrs={'placeholder': 'Ex : 97000000', 'type': 'tel'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'exemple@mail.com (optionnel)'}),
            'username':   forms.TextInput(attrs={'placeholder': "Ex : parent_dossou"}),
        }
        labels = {
            'last_name':  'Nom',
            'first_name': 'Prénom(s)',
            'phone':      'Votre numéro de téléphone',
            'email':      'Email (optionnel)',
            'username':   "Nom d'utilisateur",
        }

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password_strength(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Les mots de passe ne correspondent pas.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'parent'
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────────────────
#  FICHE ENFANT (utilisée par le parent)
# ─────────────────────────────────────────────────────────
class StudentForm(forms.ModelForm):
    class Meta:
        model  = Student
        fields = ['last_name', 'first_name', 'school', 'level']
        widgets = {
            'last_name':  forms.TextInput(attrs={'placeholder': "Nom de l'enfant"}),
            'first_name': forms.TextInput(attrs={'placeholder': "Prénom(s) de l'enfant"}),
            'school':     forms.TextInput(attrs={'placeholder': 'Ex : CEG Gbégamey'}),
            'level':      forms.Select(),
        }
        labels = {
            'last_name':  'Nom',
            'first_name': 'Prénom(s)',
            'school':     'Établissement scolaire',
            'level':      'Classe / Niveau',
        }


# ─────────────────────────────────────────────────────────
#  CONNEXION
# ─────────────────────────────────────────────────────────
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'placeholder': "Votre nom d'utilisateur",
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Votre mot de passe',
        }),
    )