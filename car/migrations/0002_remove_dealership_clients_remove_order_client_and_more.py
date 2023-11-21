# Generated by Django 4.2.7 on 2023-11-17 17:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("car", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dealership",
            name="clients",
        ),
        migrations.RemoveField(
            model_name="order",
            name="client",
        ),
        migrations.AddField(
            model_name="dealership",
            name="users",
            field=models.ManyToManyField(
                related_name="dealerships", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="car",
            name="owner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="cars",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.DeleteModel(
            name="Client",
        ),
    ]
