from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.test import APITransactionTestCase


class TestCarsAPI(APITransactionTestCase):
    fixtures = ["test_cars"]

    def tearDown(self):
        call_command("flush", interactive=False)

    def login_user(self):
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        self.client.login(username="test_user", password="test_password")

    def test_registration_failed(self):
        body = {}
        response = self.client.post("/api/register/", body)
        assert response.status_code == 400
        assert response.json() == {
            "password": ["This field is required."],
            "username": ["This field is required."],
        }

    def test_registration(self):
        body = {
            "password": "foo_password",
            "username": "foo_username",
            "email": "email@exemple.com",
        }
        response = self.client.post("/api/register/", body)
        assert response.status_code == 201
        assert response.json() == {
            "email": "email@exemple.com",
            "username": "foo_username",
        }

    def test_registration_not_valid_email(self):
        body = {
            "password": "foo_password",
            "username": "foo_username",
            "email": "email",
        }
        response = self.client.post("/api/register/", body)
        assert response.status_code == 400
        assert response.json() == {"email": ["Enter a valid email address."]}

    def test_dealerships_list(self):
        response = self.client.get("/api/dealership/")
        assert response.status_code == 200
        assert response.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"id": 1, "name": "CarShip"}],
        }

    def test_get_dealership(self):
        response = self.client.get("/api/dealership/1/")
        assert response.status_code == 200
        assert response.json() == {"id": 1, "name": "CarShip"}

    def test_get_dealership_not_found(self):
        response = self.client.get("/api/dealership/2/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_cars_list(self):
        response = self.client.get("/api/car/")
        assert response.status_code == 200
        assert response.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "car_type": {
                        "id": 1,
                        "brand": "Volkswagen",
                        "model": "Touareg",
                        "price": 35000,
                    },
                    "color": "black",
                    "year": 2020,
                    "photo": None,
                }
            ],
        }

    def test_get_car(self):
        response = self.client.get("/api/car/1/")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "car_type": {
                "id": 1,
                "brand": "Volkswagen",
                "model": "Touareg",
                "price": 35000,
            },
            "color": "black",
            "year": 2020,
            "photo": None,
        }

    def test_get_car_not_found(self):
        response = self.client.get("/api/car/2/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not found."}

    def test_get_cars_list_in_dealership(self):
        response = self.client.get("/api/dealership/1/add_car/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 1,
                "car_type": {
                    "id": 1,
                    "brand": "Volkswagen",
                    "model": "Touareg",
                    "price": 35000,
                },
                "color": "black",
                "year": 2020,
                "photo": None,
            }
        ]

    def test_get_cars_list_in_dealership_not_found(self):
        response = self.client.get("/api/dealership/2/add_car/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Dealership not found."}

    def test_get_car_in_dealership(self):
        response = self.client.get("/api/dealership/1/add_car/1/")
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "car_type": {
                "id": 1,
                "brand": "Volkswagen",
                "model": "Touareg",
                "price": 35000,
            },
            "color": "black",
            "year": 2020,
            "photo": None,
        }

    def test_get_car_not_found_in_dealership(self):
        response = self.client.get("/api/dealership/1/add_car/2/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Car not found."}

    def test_add_car_in_order(self):
        self.login_user()
        response = self.client.post("/api/dealership/1/add_car/1/")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Car 1 added in order 1",
            "url": "http://testserver/api/order/confirm/1/",
        }

    def test_add_car_in_order_not_authentication(self):
        response = self.client.post("/api/dealership/1/add_car/1/")
        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_delete_car_from_order_not_found(self):
        self.login_user()
        response = self.client.delete("/api/dealership/1/add_car/1/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Order not found."}

    def test_delete_car_from_order(self):
        self.login_user()
        add_car = self.client.post("/api/dealership/1/add_car/1/")
        assert add_car.status_code == 200
        assert add_car.json() == {
            "message": "Car 1 added in order 1",
            "url": "http://testserver/api/order/confirm/1/",
        }
        del_car = self.client.delete("/api/dealership/1/add_car/1/")
        assert del_car.status_code == 200
        assert del_car.json() == {
            "message": "Car 1 deleted from order 1",
            "url": "/api/order/confirm/1/",
        }

    def test_get_order(self):
        self.login_user()
        add_car = self.client.post("/api/dealership/1/add_car/1/")
        assert add_car.status_code == 200
        assert add_car.json() == {
            "message": "Car 1 added in order 1",
            "url": "http://testserver/api/order/confirm/1/",
        }
        confirm_order = self.client.get("/api/order/confirm/1/")
        assert confirm_order.status_code == 200
        assert confirm_order.json() == {
            "id": 1,
            "user": 1,
            "dealership": 1,
            "total": 35000,
            "car_types": [
                {
                    "car_type": {
                        "id": 1,
                        "brand": "Volkswagen",
                        "model": "Touareg",
                        "price": 35000,
                    },
                    "quantity": 1,
                }
            ],
        }

    def test_get_order_not_found(self):
        confirm_order = self.client.get("/api/order/confirm/1/")
        assert confirm_order.status_code == 404
        assert confirm_order.json() == {"detail": "Order not found."}

    def test_delete_order(self):
        self.login_user()
        add_car = self.client.post("/api/dealership/1/add_car/1/")
        assert add_car.status_code == 200
        assert add_car.json() == {
            "message": "Car 1 added in order 1",
            "url": "http://testserver/api/order/confirm/1/",
        }
        confirm_order = self.client.delete("/api/order/confirm/1/")
        assert confirm_order.status_code == 200
        assert confirm_order.json() == {"message": "The order 1 is delete"}
