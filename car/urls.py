from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include

from .views import (
    dealership_client,
    car,
    order_cart,
    order_finish,
    car_list,
    car_edit
)

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("", dealership_client, name="dealership_client"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("car/dealer_id=<int:dealership_id>/user_id=<int:user_id>/", car, name="car"),
    path("car/dealer_id=<int:dealership_id>", car_list, name="car_list"),
    path("order_cart/order_id=<int:order_id>/", order_cart, name="order_cart"),
    path("order_finish/order_id=<int:order_id>/", order_finish, name="order_finish"),
    path("car_edit/car_id=<int:car_id>/dealer_id=<int:dealership_id>/user_id=<int:user_id>/", car_edit, name="car_edit"),
]
