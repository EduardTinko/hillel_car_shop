from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from faker import Faker
from rest_framework import viewsets, status, mixins
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CarForm
from .invoice import create_invoice, verify_signature
from .models import Car, Dealership, Order, OrderQuantity, Licence
from .permissions import IsOwner
from .serializers import (
    DealershipSerializer,
    CarSerializer,
    OrderSerializer,
    UserSerializer,
    InfoAddCarSerializer,
)

# Create your views here.

fake = Faker()


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
        create_invoice(order, request.build_absolute_uri(reverse("webhook-mono")))
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
        except Exception:
            return Response({"status": "error"}, status=400)
        reference = request.data.get("reference")
        order = Order.objects.get(id=reference)
        if order.order_id != request.data.get("invoiceId"):
            return Response({"status": "error"}, status=400)
        cars = Car.objects.filter(blocked_by_order=order.id)
        for car_item in cars:
            car_item.sell()
            car_item.unblock()
            generate_license(car_item)
        order.is_paid = True
        order.save()
        return Response({"status": "ok"})


def dealership_client(request):
    user = request.user
    dealerships = Dealership.objects.all()
    if request.method == "GET":
        context = {"dealerships": dealerships, "user": user}
        return render(request, "dealership_client.html", context)

    if "view_cars" in request.POST:
        user_id = user.id
        dealership_id = request.POST.get("dealership")
        if not user_id:
            return redirect(reverse("car_list", args=[dealership_id]))
        return redirect(reverse("car", args=(dealership_id, user_id)))
    return render(
        request, "dealership_client.html", {"dealerships": dealerships, "user": user}
    )


@login_required
def car(request, dealership_id, user_id):
    user = User.objects.get(id=user_id)
    dealership = Dealership.objects.get(id=dealership_id)
    order, is_created = Order.objects.get_or_create(
        user=user, dealership=dealership, is_paid=False
    )
    cars = Car.objects.filter(dealerships=dealership, owner__isnull=True)

    if request.method == "GET":
        cars_in_order = len(Car.objects.filter(blocked_by_order=order.id))
        context = {"order": order, "cars": cars, "cars_in_order": cars_in_order}
        return render(request, "car.html", context)

    if "ad_car" in request.POST:
        ad_car_id = request.POST.get("ad_car")
        add_car_in_order(ad_car_id, order)
        cars_in_order = len(Car.objects.filter(blocked_by_order=order.id))
        context = {"order": order, "cars": cars, "cars_in_order": cars_in_order}
        return render(request, "car.html", context)

    if "car_edit" in request.POST:
        car_id = int(request.POST.get("car_edit"))
        return redirect(reverse("car_edit", args=(car_id, dealership_id, user_id)))

    if "create_order" in request.POST:
        order_id = order.id
        return redirect(reverse("order_cart", args=[order_id]))
    return HttpResponse("Bad request", status=400)


def car_list(request, dealership_id):
    dealership = Dealership.objects.get(id=dealership_id)
    cars = Car.objects.filter(dealerships=dealership, owner__isnull=True)
    if request.method == "GET":
        return render(
            request, "car_list.html", {"cars": cars, "dealership": dealership}
        )
    return HttpResponse("Bad request", status=400)


def car_edit(request, car_id, dealership_id, user_id):
    edited_car = Car.objects.get(id=car_id)
    if request.method == "GET":
        form = CarForm(instance=edited_car)
        return render(request, "car_edit.html", {"form": form})
    form = CarForm(request.POST, request.FILES, instance=edited_car)
    if form.is_valid():
        form.save()
        return redirect(reverse("car", args=(dealership_id, user_id)))
    return render(request, "car_edit.html", {"car": edited_car, "form": form})


def add_car_in_order(ad_car_id, order):
    quantity = 1
    added_car = Car.objects.get(id=ad_car_id)
    added_car.block(order)
    order_quantity, is_created = OrderQuantity.objects.get_or_create(
        car_type=added_car.car_type, quantity=quantity, order=order
    )

    if not is_created:
        order_quantity.quantity += 1
        order_quantity.save()


@login_required
def order_cart(request, order_id):
    order = Order.objects.get(id=order_id)
    cars_in_order = Car.objects.filter(blocked_by_order__id=order.id)
    total_price = (
        cars_in_order.aggregate(Sum("car_type__price"))["car_type__price__sum"] or 0
    )
    context = {
        "order": order,
        "cars_in_order": cars_in_order,
        "total_price": total_price,
    }
    if request.method == "GET":
        return render(request, "order_cart.html", context)

    if "pay_order" in request.POST:
        create_invoice(order, reverse("webhook-mono"))
        return Response({"invoice_url": order.invoice_url})

    if "car_list" in request.POST:
        return redirect(reverse("car", args=(order.dealership.id, order.user.id)))

    if "clear_cart" in request.POST:
        for car_in_order in cars_in_order:
            car_in_order.unblock()
        return redirect(reverse("order_cart", args=[order.id]))

    if "delete_car" in request.POST:
        delete_car_id = request.POST.get("delete_car")
        deleted_car = Car.objects.get(id=delete_car_id)
        deleted_car.unblock()
        return redirect(reverse("order_cart", args=[order.id]))
    return HttpResponse("Bad request", status=400)


def order_finish(request, order_id):
    order = Order.objects.get(id=order_id)
    sell_cars = Car.objects.filter(owner=order.user.id)
    if request.method == "GET":
        return render(
            request, "order_finish.html", {"sell_cars": sell_cars, "order": order}
        )

    if "car_list" in request.POST:
        return redirect(reverse("car", args=(order.dealership.id, order.user.id)))
    return HttpResponse("Bad request", status=400)


def generate_license(sell_car):
    car_license = (
        f"{fake.random_uppercase_letter() * 2} "
        f"{fake.random_int(min=1000, max=9999)}"
        f" {fake.random_uppercase_letter() * 2}"
    )
    licence, create = Licence.objects.get_or_create(car=sell_car, number=car_license)
    licence.save()
