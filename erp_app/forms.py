"""
ERP Application Forms
"""
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from .models import SupplierEvaluation, Supplier


class SupplierEvaluationForm(forms.ModelForm):
    """Form for adding supplier evaluation"""
    rating = forms.DecimalField(
        max_digits=3,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('5.00'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'max': '5'
        }),
        help_text='Rating from 0.0 to 5.0'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Optional evaluation notes...'
        })
    )

    class Meta:
        model = SupplierEvaluation
        fields = ['rating', 'notes']
        labels = {
            'rating': 'Rating (0.0 - 5.0)',
            'notes': 'Evaluation Notes (Optional)'
        }

