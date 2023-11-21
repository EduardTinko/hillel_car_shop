from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from faker import Faker

from .forms import CustomUserCreationForm
from .models import Car, Dealership, Order, OrderQuantity, Licence

# Create your views here.

fake = Faker()


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


def logout(request):
    logout(request)
    return redirect("register")


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
    cars = Car.objects.filter(car_type__dealerships=dealership, owner__isnull=True)

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

    if "create_order" in request.POST:
        order_id = order.id
        return redirect(reverse("order_cart", args=[order_id]))
    return HttpResponse("Bad request", status=400)


def car_list(request, dealership_id):
    dealership = Dealership.objects.get(id=dealership_id)
    cars = Car.objects.filter(car_type__dealerships=dealership, owner__isnull=True)
    if request.method == "GET":
        return render(
            request, "car_list.html", {"cars": cars, "dealership": dealership}
        )
    return HttpResponse("Bad request", status=400)


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
            for car_in_order in cars_in_order:
                car_in_order.sell()
                car_in_order.unblock()
                generate_license(car_in_order)
            order.is_paid = True
            order.save()
            return redirect(reverse("order_finish", args=[order.id]))
        return render(request, "order_cart.html", context)

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
