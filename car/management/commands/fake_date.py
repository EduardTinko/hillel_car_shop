import random
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from ...models import Car, CarType, Dealership, Licence, Order, OrderQuantity

fake = Faker("uk_UA")

cars = [
    ["Volkswagen", "Touareg", 2500000, 2024, "car/static/VWTouareg.png"],
    ["Volkswagen", "Arteon", 1800000, 2023, "car/static/VWArteon.png"],
    ["Volkswagen", "Golf GTI", 1650000, 2022, "car/static/VWGolfGTI.png"],
    ["Volkswagen", "Tiguan", 1600000, 2022, "car/static/VWTiguan.png"],
    ["Ford", "Ranger", 1950000, 2024, "car/static/fordranger.png"],
    ["Ford", "Puma", 1500000, 2021, "car/static/fordpuma.png"],
    ["Ford", "Focus", 1700000, 2022, "car/static/fordfocus.png"],
]

color = ["Red", "Silver", "Blue", "Yellow", "Black", "White"]

dealer_ship_names = [
    "Volkswagen",
    "Ford",
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

        for dealer in dealer_ship_names:
            Dealership.objects.create(name=dealer)
        dealerships = Dealership.objects.all()
        for item in cars:
            car_type = CarType.objects.create(
                brand=item[0], model=item[1], price=item[2]
            )
            for dealership in dealerships:
                if car_type.brand == dealership.name:
                    for _ in range(5):
                        car = Car.objects.create(
                            car_type=car_type,
                            color=random.choice(color),
                            year=item[3],
                        )
                        with open(item[4], "rb") as file:
                            car.photo.save(item[4], file)
                        dealership.available_car.add(car)
                        dealership.save()

        self.stdout.write(self.style.SUCCESS("База даних оновлена!"))
