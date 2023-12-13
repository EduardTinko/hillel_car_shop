from allauth.account.forms import LoginForm, SignupForm
from django import forms
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .models import Car, CarType, Dealership, Order, OrderQuantity, Licence


class MyCustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].help_text = ""


class MyCustomLoginForm(LoginForm):
    remember = forms.BooleanField(label=_("Запам'ятати мене"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            reset_url = reverse("account_reset_password")
        except NoReverseMatch:
            pass
        else:
            forgot_txt = _("<p> Забули пароль?")
            self.fields["password"].help_text = mark_safe(
                f'<a href="{reset_url}">{forgot_txt}</a>'
            )


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
