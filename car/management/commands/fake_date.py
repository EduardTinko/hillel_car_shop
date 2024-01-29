import json
import os
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from ...models import Car, CarType, Dealership, Licence, Order, OrderQuantity

fake = Faker("uk_UA")

car_brands_and_models = [
    ["Toyota", "Camry"],
    ["Toyota", "Corolla"],
    ["Toyota", "Rav4"],
    ["Honda", "Civic"],
    ["Honda", "Accord"],
    ["Honda", "CR-V"],
    ["Ford", "Fusion"],
    ["Ford", "Focus"],
    ["Ford", "Escape"],
    ["Chevrolet", "Malibu"],
    ["Chevrolet", "Cruze"],
    ["Chevrolet", "Equinox"],
]

color = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple", "Pink", "Black", "White"]

dealer_ship_names = [
    "Авто Еліт",
    "Імперське Авто",
    "Професійне Авто",
    "Авто Експрес",
    "Авто Преміум",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.all().delete()
        Car.objects.all().delete()
        CarType.objects.all().delete()
        Dealership.objects.all().delete()
        Licence.objects.all().delete()
        OrderQuantity.objects.all().delete()
        Order.objects.all().delete()

        password = os.getenv("DJANGO_ADMIN_PASSWORD", "admin")

        User.objects.create_user(
            username="admin", email="admin@admin.com", password=password, is_staff=True
        )

        for item in car_brands_and_models:
            random_price = random.randint(10000, 50000)

            CarType.objects.create(brand=item[0], model=item[1], price=random_price)

        cars_type = CarType.objects.all()
        for car_type in cars_type:
            for _ in range(3):
                Car.objects.create(
                    car_type=car_type,
                    color=random.choice(color),
                    year=random.randint(2015, 2023),
                )

        for dealer in dealer_ship_names:
            new_dealership = Dealership.objects.create(name=dealer)
            available_cars = Car.objects.all()
            k = random.randint(4, 10)
            selected_brands = random.sample(list(available_cars), k=k)
            new_dealership.available_car.set(selected_brands)

        data = {"fasda": "dasdasd"}

        if data:
            with open("google_storage.json", "w") as json_file:
                json.dump(data, json_file, indent=None)
