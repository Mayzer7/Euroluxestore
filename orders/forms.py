from django import forms

class CreateOrderForm(forms.Form):

    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField()
    requires_delivery = forms.ChoiceField(
        choices=[
            ("0", 'False'),
            ("1", 'True'),
        ]
    )
    delivery_address = forms.CharField(required=False)
    payment_on_get = forms.ChoiceField(
        choices=[
            ("0", 'False'),
            ("1", 'True'),
        ]
    )

    # # С помощью приставки clean_ можно создавать собственные валидаторы
    # def clean_phone_number(self): 
    #     data = self.cleaned_data['phone_number']

    #     if not data.isdigit():
    #         raise forms.ValidationError("Номер телефона должен содеражть только цифры")
        
    #     if len(data) > 10:
    #         raise forms.ValidationError("Номер телефона не может содержать больше 10 символов")

    #     if len(data) < 10:
    #         raise forms.ValidationError("Номер телефона не может содержать меньше 10 символов")
        
    #     return data