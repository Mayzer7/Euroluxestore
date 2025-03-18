import re
from django import forms
from .models import Order
from django.core.exceptions import ValidationError

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'delivery_method', 'address']

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if phone:
            # Разрешаем только цифры и + в начале
            if not re.match(r'^\+?\d{7,15}$', phone):
                raise ValidationError("Введите корректный номер телефона (7-15 цифр, можно с +).")

        return phone