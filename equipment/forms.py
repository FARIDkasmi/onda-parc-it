from django import forms
from .models import Equipment

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['code_inventaire', 'designation', 'categorie', 'emplacement', 'statut']
        widgets = {
            'code_inventaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: ONDA-PC-012'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Ecran Affichage Vols (FIDS)'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'emplacement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Zone Sûreté / Inspection Filtrage'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }