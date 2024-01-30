from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from faker import Faker
from rest_framework.response import Response

from .forms import DealershipForm, CarForm, CarTypeForm
from .invoice import create_invoice
from .models import Car, Dealership, Order, OrderQuantity, Licence, CarType

# Create your views here.

fake = Faker()


def dealership_client(request):
    user = request.user
    dealerships = Dealership.objects.all()
    context = {"dealerships": dealerships, "user": user}
    if request.method == "GET":
        return render(request, "dealership_client.html", context)

    if "view_cars" in request.POST:
        dealership_id = request.POST.get("view_cars")
        return redirect(reverse("car", args=[dealership_id]))
    if "delete" in request.POST:
        dealership_id = request.POST.get("delete")
        dealership = Dealership.objects.get(id=[dealership_id])
        dealership.delete()
    if "edit" in request.POST:
        dealership_id = request.POST.get("edit")
        return redirect(reverse(edit_dealership, args=[dealership_id]))
    return render(request, "dealership_client.html", context)


def car(request, dealership_id):
    dealership = Dealership.objects.get(id=dealership_id)

    if not request.user.is_authenticated:
        cars = Car.objects.filter(dealerships=dealership, owner__isnull=True)
        if request.method == "GET":
            context = {"dealership": dealership, "cars": cars}
            return render(request, "car.html", context)

    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        order, is_created = Order.objects.get_or_create(
            user=user, dealership=dealership, is_paid=False
        )
        cars = Car.objects.filter(dealerships=dealership, owner__isnull=True)

        if request.method == "GET":
            cars_in_order = len(Car.objects.filter(blocked_by_order=order.id))
            context = {
                "dealership": dealership,
                "order": order,
                "cars": cars,
                "cars_in_order": cars_in_order,
            }
            return render(request, "car.html", context)

        if "ad_car" in request.POST:
            ad_car_id = request.POST.get("ad_car")
            add_car_in_order(ad_car_id, order)
            cars_in_order = len(Car.objects.filter(blocked_by_order=order.id))
            context = {
                "dealership": dealership,
                "order": order,
                "cars": cars,
                "cars_in_order": cars_in_order,
            }
            return render(request, "car.html", context)

        if "car_edit" in request.POST:
            car_id = int(request.POST.get("car_edit"))
            return redirect(reverse("car_edit", args=(car_id, dealership_id)))

        if "new_car" in request.POST:
            return redirect(reverse("create_car", args=[dealership_id]))

        if "create_order" in request.POST:
            order_id = order.id
            return redirect(reverse("order_cart", args=[order_id]))
        if "delete" in request.POST:
            car_id = request.POST.get("delete")
            Car.objects.get(id=car_id).delete()
            return redirect(reverse("car", args=[order.dealership.id]))
        return HttpResponse("Bad request", status=400)


@login_required
def car_edit(request, car_id, dealership_id):
    edited_car = Car.objects.get(id=car_id)
    if request.method == "GET":
        form = CarForm(instance=edited_car)
        return render(request, "car_edit.html", {"form": form})
    form = CarForm(request.POST, request.FILES, instance=edited_car)
    if form.is_valid():
        form.save()
        dealerships = request.POST.getlist("dealerships")
        for dealership_id in dealerships:
            dealership = Dealership.objects.get(id=dealership_id)
            dealership.available_car.add(car_id)
        return redirect(reverse("car", args=[dealership_id]))
    return render(request, "car_edit.html", {"form": form})


@login_required
def create_car(request):
    if not request.user.is_staff:
        return redirect("account_login")
    if request.method == "GET":
        form = CarForm()
        return render(request, "car_edit.html", {"form": form})
    form = CarForm(request.POST, request.FILES)
    if form.is_valid():
        dealerships = request.POST.getlist("dealerships")
        new_car = form.save()
        for dealership_id in dealerships:
            dealership = Dealership.objects.get(id=dealership_id)
            dealership.available_car.add(new_car.id)
        return render(
            request, "car_edit.html", {"form": form, "massage": "Додано автомобіль"}
        )
    return render(request, "car_edit.html", {"form": form})


@login_required
def list_car_type(request):
    if not request.user.is_staff:
        return redirect("account_login")
    car_types = CarType.objects.all()
    if request.method == "GET":
        return render(request, "car_type.html", {"car_types": car_types})
    if "edit" in request.POST:
        car_type_id = request.POST.get("edit")
        return redirect(reverse("edit_car_type", args=[car_type_id]))
    if "delete" in request.POST:
        car_type_id = request.POST.get("delete")
        CarType.objects.get(id=car_type_id).delete()
    return render(request, "car_type.html", {"car_types": car_types})


@login_required
def edit_car_type(request, car_type_id):
    car_type = CarType.objects.get(id=car_type_id)
    if not request.user.is_staff:
        return redirect("account_login")
    if request.method == "GET":
        form = CarTypeForm(instance=car_type)
        return render(request, "car_edit.html", {"form": form})
    form = CarTypeForm(request.POST, instance=car_type)
    if form.is_valid():
        form.save()
        return redirect(reverse("list_car_type"))
    return render(request, "car_edit.html", {"form": form})


@login_required
def create_car_type(request):
    if not request.user.is_staff:
        return redirect("account_login")
    if request.method == "GET":
        form = CarTypeForm()
        return render(request, "car_edit.html", {"form": form})
    form = CarTypeForm(request.POST)
    if form.is_valid():
        form.save()
        return render(
            request, "car_edit.html", {"form": form, "massage": "Зміни збережено"}
        )
    return render(request, "car_edit.html", {"form": form})


@login_required
def create_dealership(request):
    if not request.user.is_staff:
        return redirect("account_login")
    if request.method == "GET":
        form = DealershipForm()
        return render(request, "car_edit.html", {"form": form})
    form = DealershipForm(request.POST)
    if form.is_valid():
        form.save()
        return render(
            request,
            "car_edit.html",
            {"form": form, "massage": "Додано дилерський центр"},
        )
    return render(request, "car_edit.html", {"form": form})


@login_required
def edit_dealership(request, dealership_id):
    if not request.user.is_staff:
        return redirect("account_login")
    dealership = Dealership.objects.get(id=dealership_id)
    if request.method == "GET":
        form = DealershipForm(instance=dealership)
        return render(request, "car_edit.html", {"form": form})
    form = DealershipForm(request.POST, instance=dealership)
    if form.is_valid():
        form.save()
        return redirect(reverse("dealership_client"))
    return render(request, "car_edit.html", {"form": form})


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
        if total_price != 0:
            create_invoice(order, request.build_absolute_uri(reverse("webhook-mono")))
            return Response({"invoice_url": order.invoice_url})
        else:
            return render(request, "order_cart.html", context)

    if "car_list" in request.POST:
        return redirect(reverse("car", args=[order.dealership.id]))

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


def order_finish(request, user_id):
    sell_cars = Car.objects.filter(owner=user_id)
    if request.method == "GET":
        return render(request, "order_finish.html", {"sell_cars": sell_cars})
    return HttpResponse("Bad request", status=400)


def generate_license(sell_car):
    car_license = (
        f"{fake.random_uppercase_letter() * 2} "
        f"{fake.random_int(min=1000, max=9999)}"
        f" {fake.random_uppercase_letter() * 2}"
    )
    licence, create = Licence.objects.get_or_create(car=sell_car, number=car_license)
    licence.save()
