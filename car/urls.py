from django.urls import path

from .views import dealership_client, car, order_cart, order_finish

urlpatterns = [
    path("", dealership_client, name="dealership_client"),
    path(
        "car/dealer_id=<int:dealership_id>/client_id=<int:client_id>/", car, name="car"
    ),
    path("order_cart/order_id=<int:order_id>/", order_cart, name="order_cart"),
    path("order_finish/order_id=<int:order_id>/", order_finish, name="order_finish"),
]
