import rest_framework.authtoken.views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.views import APIView

from . import views
from .views import dealership_client, car, order_cart, order_finish, car_list, car_edit


class DocsView(APIView):
    def get(self, request, *args, **kwargs):
        apidocs = {
            "register": request.build_absolute_uri("api/register"),
            "dealership": request.build_absolute_uri("api/dealership"),
            "car": request.build_absolute_uri("api/car"),
            "add_car_list": request.build_absolute_uri(
                "api/dealership/*/add_car/",
            ),
            "add_car": request.build_absolute_uri("api/dealership/*/add_car/*/"),
            "confirm": request.build_absolute_uri("api/order/confirm/*/"),
        }
        return Response(apidocs)


router = routers.DefaultRouter()
router.register("api/dealership", views.DealershipViewSet)
router.register("api/car", views.CarViewSet)
router.register("api/register", views.UserRegisterViewSet)


urlpatterns = [
    path("", DocsView.as_view()),
    path("api/order/confirm/<int:order_id>/", views.ConfirmOrderAPIView.as_view()),
    path(
        "api/dealership/<int:dealer_id>/add_car/",
        views.AddCarAPIView.as_view(http_method_names="get"),
    ),
    path(
        "api/dealership/<int:dealer_id>/add_car/<int:car_id>/",
        views.AddCarAPIView.as_view(http_method_names=["post", "delete", "get"]),
    ),
    path("accounts/", include("allauth.urls")),
    path("dealership/", dealership_client, name="dealership_client"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("car/dealer_id=<int:dealership_id>/user_id=<int:user_id>/", car, name="car"),
    path("car/dealer_id=<int:dealership_id>", car_list, name="car_list"),
    path("order_cart/order_id=<int:order_id>/", order_cart, name="order_cart"),
    path("order_finish/order_id=<int:order_id>/", order_finish, name="order_finish"),
    path(
        "car_edit/car_id=<int:car_id>/dealer_id=<int:dealership_id>/user_id=<int:user_id>/",
        car_edit,
        name="car_edit",
    ),
    path("api-token-auth/", rest_framework.authtoken.views.obtain_auth_token),
    path("api/auth/", include("rest_framework.urls")),
]

urlpatterns += router.urls
