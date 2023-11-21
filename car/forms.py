from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Car, CarType, Dealership, Order, OrderQuantity, Licence


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].help_text = ""

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class CarTypeForm(forms.Form):
    class Meta:
        model = CarType
        fields = ["brand", "model", "price"]


class CarForm(forms.Form):
    model = Car
    fields = ["car_type", "color", "year", "blocked_by_order", "owner"]


class LicenceForm(forms.Form):
    model = Licence
    fields = ["car", "number"]


class DealershipForm(forms.Form):
    model = Dealership
    fields = ["name", "available_car_type", "users"]


class OrderForm(forms.Form):
    model = Order
    fields = ["user", "dealership", "is_paid"]


class OrderQuantityForm(forms.Form):
    model = OrderQuantity
    fields = ["car_type", "quantity", "order"]
