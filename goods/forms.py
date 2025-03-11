from django import forms
from .models import Review
from django.core.exceptions import ValidationError
from django.contrib import messages

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image_1', 'image_2', 'image_3']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if not comment:
            raise ValidationError("Поле с комментарием не может быть пустым.")
        return comment
