import rest_framework.authtoken.views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.views import APIView

from . import api_views
from .views import (
    dealership_client,
    car,
    order_cart,
    order_finish,
    car_edit,
    create_car,
    create_dealership,
    create_car_type,
    edit_dealership,
    list_car_type,
    edit_car_type,
)


class DocsView(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        apidocs = {
            "register": request.build_absolute_uri("register"),
            "dealership": request.build_absolute_uri("dealership"),
            "car": request.build_absolute_uri("car"),
        }
        return Response(apidocs)


router = routers.DefaultRouter()

router.register("api/dealership", api_views.DealershipViewSet)
router.register("api/car", api_views.CarViewSet)
router.register("api/register", api_views.UserRegisterViewSet)

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", dealership_client, name="dealership_client"),
    path("car/dealer_id=<int:dealership_id>/", car, name="car"),
    path("order_cart/order_id=<int:order_id>/", order_cart, name="order_cart"),
    path("order_finish/user_id=<int:user_id>/", order_finish, name="order_finish"),
    path(
        "edit_dealership/dealership_id=<int:dealership_id>/",
        edit_dealership,
        name="edit_dealership",
    ),
    path("create_car/", create_car, name="create_car"),
    path(
        "car_edit/car_id=<int:car_id>/dealership_id=<int:dealership_id>/",
        car_edit,
        name="car_edit",
    ),
    path("list_car_type/", list_car_type, name="list_car_type"),
    path("create_car_type/", create_car_type, name="create_car_type"),
    path(
        "edit_car_type/car_type_id=<int:car_type_id>/",
        edit_car_type,
        name="edit_car_type",
    ),
    path("create_dealership/", create_dealership, name="create_dealership"),
]

urlpatterns += [
    path("api/", DocsView.as_view(), name="docs-view"),
    path("api/order/confirm/<int:order_id>/", api_views.ConfirmOrderAPIView.as_view(), name="order_confirm"),
    path(
        "api/dealership/<int:dealer_id>/add_car/",
        api_views.AddCarAPIView.as_view(http_method_names="get"),
    ),
    path("api-token-auth/", rest_framework.authtoken.views.obtain_auth_token),
    path("api/auth/", include("rest_framework.urls")),
    path(
        "webhook-mono/",
        api_views.MonoAcquiringWebhookReceiver.as_view(),
        name="webhook-mono",
    ),
    path(
        "api/dealership/<int:dealer_id>/add_car/<int:car_id>/",
        api_views.AddCarAPIView.as_view(),
    ),
]

urlpatterns += router.urls
