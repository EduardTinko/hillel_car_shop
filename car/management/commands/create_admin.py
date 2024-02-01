import os

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from ...models import Car, CarType, Dealership, Licence, Order, OrderQuantity


class Command(BaseCommand):
    def handle(self, *args, **options):
        password = os.getenv("DJANGO_ADMIN_PASSWORD", "admin")
        try:
            user = User.objects.create_user(
                username="admin",
                email="admin@admin.com",
                password=password,
                is_staff=True,
            )
            email, _ = EmailAddress.objects.get_or_create(user=user)
            email.verified = True
            email.primary = True
            email.save()
            self.stdout.write(self.style.SUCCESS("Admin created successfully"))
        except Exception as e:
            self.stderr.write(f"Error: {e}")
