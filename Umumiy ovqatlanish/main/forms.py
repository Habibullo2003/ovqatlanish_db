from django import forms
from .models import Buyurtma

class BuyurtmaForm(forms.ModelForm):
    class Meta:
        model = Buyurtma
        fields = ['mijoz', 'restoran', 'taomlar', 'manzil']
        labels = {
            'mijoz': 'mijoz',
            'restoran': 'Restoran',
            'taomlar': 'Tanlangan taomlar',
            'manzil': 'Manzil',
        }
        widgets = {
            'mijoz': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'restoran': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'taomlar': forms.CheckboxSelectMultiple(attrs={'class': 'form-check taomlar-grid'}),
            'manzil': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Manzilni kiriting',
                'required': True
            })
        }



