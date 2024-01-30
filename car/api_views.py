from django.contrib.auth.models import User
import rest_framework.reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, mixins
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .invoice import create_invoice, verify_signature
from .models import Car, Dealership, Order, OrderQuantity
from .permissions import IsOwner
from .serializers import (
    DealershipSerializer,
    CarSerializer,
    OrderSerializer,
    UserSerializer,
    InfoAddCarSerializer,
)
from .views import generate_license


class DealershipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dealership.objects.all()
    serializer_class = DealershipSerializer
    http_method_names = ["get"]


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    http_method_names = ["get"]


class UserRegisterViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@method_decorator(csrf_exempt, name="dispatch")
class AddCarAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def _get_dealership(self, dealer_id):
        try:
            return Dealership.objects.get(pk=dealer_id)
        except Dealership.DoesNotExist:
            raise NotFound(
                detail="Dealership not found.", code=status.HTTP_404_NOT_FOUND
            )

    def _get_car(self, car_id, dealership, blocked_by_order):
        try:
            return Car.objects.get(
                id=car_id,
                owner=None,
                blocked_by_order=blocked_by_order,
                dealerships=dealership,
            )
        except Car.DoesNotExist:
            raise NotFound(detail="Car not found.", code=status.HTTP_404_NOT_FOUND)

    def _get_order(self, user, dealership):
        try:
            return Order.objects.get(user=user, is_paid=False, dealership=dealership)
        except Order.DoesNotExist:
            raise NotFound(detail="Order not found.", code=status.HTTP_404_NOT_FOUND)

    def get(self, request, dealer_id, car_id=None, *args, **kwargs):
        dealership = self._get_dealership(dealer_id=dealer_id)
        if car_id:
            cars = self._get_car(
                car_id=car_id, dealership=dealership, blocked_by_order=None
            )
            serialized_order = CarSerializer(cars)
        else:
            cars = Car.objects.filter(
                dealerships=dealership, blocked_by_order=None, owner_id=None
            )
            serialized_order = CarSerializer(cars, many=True)
        return Response(serialized_order.data, status=status.HTTP_200_OK)

    def post(self, request, dealer_id, car_id, *args, **kwargs):
        user = request.user
        dealership = self._get_dealership(dealer_id)
        added_car = self._get_car(
            car_id=car_id, dealership=dealership, blocked_by_order=None
        )
        order, create = Order.objects.get_or_create(
            user=user, is_paid=False, dealership=dealership
        )
        added_car.block(order)
        order.total += added_car.car_type.price
        order_quantity, is_created = OrderQuantity.objects.get_or_create(
            car_type=added_car.car_type, order=order
        )
        order.car_types.add(order_quantity)
        order.save()
        serialized_order = InfoAddCarSerializer(
            {
                "message": f"Car {added_car.pk} added in order {order.id}",
                "url": f"/api/order/confirm/{order.id}/",
            }
        )
        return Response(serialized_order.data, status=status.HTTP_200_OK)

    def delete(self, request, dealer_id, car_id, *args, **kwargs):
        user = request.user
        dealership = self._get_dealership(dealer_id=dealer_id)
        order = self._get_order(dealership=dealership, user=user)
        deleted_car = self._get_car(
            car_id=car_id, dealership=dealership, blocked_by_order=order.id
        )
        deleted_car.unblock()
        order.total -= deleted_car.car_type.price
        OrderQuantity.objects.get(car_type=deleted_car.car_type, order=order).delete()
        order.save()
        serialized_order = InfoAddCarSerializer(
            {
                "message": f"Car {deleted_car.pk} deleted from order {order.id}",
                "url": f"/api/order/confirm/{order.id}/",
            }
        )
        return Response(serialized_order.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class ConfirmOrderAPIView(APIView):
    permission_classes = [IsOwner]

    def _get_order(self, order_id):
        try:
            return Order.objects.get(id=order_id, is_paid=False)
        except Order.DoesNotExist:
            raise NotFound(detail="Order not found.", code=status.HTTP_404_NOT_FOUND)

    def get(self, request, order_id, *args, **kwargs):
        order = self._get_order(order_id=order_id)
        self.check_object_permissions(request, order)
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status=status.HTTP_200_OK)

    def post(self, request, order_id, *args, **kwargs):
        order = self._get_order(order_id=order_id)
        self.check_object_permissions(request, order)
        create_invoice(
            order,
            redirect=f"/api/",
            webhook_url=rest_framework.reverse.reverse("webhook-mono", request=request),
            request=request,
        )
        return Response({"invoice_url": order.invoice_url})

    def delete(self, request, order_id, *args, **kwargs):
        order = self._get_order(order_id=order_id)
        self.check_object_permissions(request, order)
        if not order.is_paid:
            cars = Car.objects.filter(blocked_by_order=order.id)
            if cars:
                for car_item in cars:
                    car_item.unblock()
            order.delete()
        return Response(
            {"message": f"The order {order_id} is delete"}, status=status.HTTP_200_OK
        )


class MonoAcquiringWebhookReceiver(APIView):
    def post(self, request):
        try:
            verify_signature(request)
        except Exception as e:
            return Response({"status": "error"}, status=400)
        reference = int(request.data.get("reference"))
        order = Order.objects.get(id=reference)
        if order.order_id != request.data.get("invoiceId"):
            return Response({"status": "error"}, status=400)
        if request.data.get("status") == "success":
            cars = Car.objects.filter(blocked_by_order=order.id)
            for car_item in cars:
                car_item.sell()
                car_item.unblock()
                generate_license(car_item)
            order.is_paid = True
            order.save()
            return Response({"status": "ok"})
        return Response({"status": "error"}, status=400)
