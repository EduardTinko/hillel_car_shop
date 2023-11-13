from django import forms

from .models import Car, CarType, Client, Dealership, Order, OrderQuantity, Licence


class ClientForm(forms.Form):
    class Meta:
        model = Client
        fields = ["name", "email", "phone"]


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
    fields = ["name", "available_car_type", "clients"]


class OrderForm(forms.Form):
    model = Order
    fields = ["client", "dealership", "is_paid"]


class OrderQuantityForm(forms.Form):
    model = OrderQuantity
    fields = ["car_type", "quantity", "order"]
