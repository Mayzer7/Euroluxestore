from django import forms
from .models import Review
from django.core.exceptions import ValidationError
from django.contrib import messages

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '★☆☆☆☆ Ужасно'),
        (2, '★★☆☆☆ Плохо'),
        (3, '★★★☆☆ Нормально'),
        (4, '★★★★☆ Хорошо'),
        (5, '★★★★★ Отлично'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'})
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image_1', 'image_2', 'image_3']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ваш отзыв поможет другим пользователям сделать выбор!'}),
        }


    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if not comment:
            raise ValidationError("Поле с комментарием не может быть пустым.")
        return comment
