# coding: utf-8
from django import forms


class TrackForm(forms.Form):
    CHOICES = (
        ('Vélo de route', 'Vélo de route'),
        ('VTT', 'VTT'),
        ('Marche à pied', 'Marche à pied'),
        ('Moto', 'Moto'),
        ('Voiture', 'Voiture'),
        ('Autre', 'Autre...'),
    )
    title = forms.CharField(max_length=100)
    type = forms.ChoiceField(label='Parcours de', choices=CHOICES)
    description = forms.CharField(widget=forms.Textarea, max_length=2048)


class UploadForm(TrackForm):
    fichier = forms.FileField()


class QuickLoginForm(forms.Form):
    username = forms.CharField(required=False, max_length=20, label='username')
    password = forms.CharField(required=False, max_length=20, widget=forms.PasswordInput, label='pass')


class QuickSearchForm(forms.Form):
    recherche = forms.CharField(required=False, max_length=10, label='recherche', initial="Rechercher",
                                widget=forms.TextInput(attrs={'onclick': 'this.select();', }))

