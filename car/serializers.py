from rest_framework import serializers

from .models import CarType, Car, Licence, Dealership, Order, OrderQuantity
from django.contrib.auth.models import User


class CarTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = ["id", "brand", "model", "price"]


class CarSerializer(serializers.ModelSerializer):
    car_type = CarTypeSerializer(read_only=True)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Car
        fields = ["id", "car_type", "color", "year", "photo"]


class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licence
        fields = ["car", "number"]


class DealershipSerializerName(serializers.ModelSerializer):
    class Meta:
        model = Dealership
        fields = ["id", "name"]


class OrderQuantitySerializer(serializers.ModelSerializer):
    car_type = CarTypeSerializer()

    class Meta:
        model = OrderQuantity
        fields = ["car_type", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    car_types = OrderQuantitySerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "user", "dealership", "car_types", "total"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["password", "username", "email"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class InfoAddCarSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100)
    url = serializers.CharField(max_length=100)


class ListOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.IntegerField()
    dealership = serializers.IntegerField()
    cars = CarSerializer(many=True)
    total = serializers.IntegerField()
