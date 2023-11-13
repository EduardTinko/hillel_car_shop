import random

from django.core.management.base import BaseCommand
from faker import Faker

from ...models import Car, CarType, Client, Dealership, Licence, Order, OrderQuantity

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
        Client.objects.all().delete()
        Car.objects.all().delete()
        CarType.objects.all().delete()
        Dealership.objects.all().delete()
        Licence.objects.all().delete()
        OrderQuantity.objects.all().delete()
        Order.objects.all().delete()

        for _ in range(5):
            random_name = fake.name()
            random_email = fake.email()
            random_phone = fake.phone_number()

            Client.objects.create(
                name=random_name, email=random_email, phone=random_phone
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
            available_brands = CarType.objects.all()
            k = random.randint(4, 10)
            selected_brands = random.sample(list(available_brands), k=k)
            new_dealership.available_car_types.set(selected_brands)

        self.stdout.write(self.style.SUCCESS("Базу даних успішно заповнено"))
