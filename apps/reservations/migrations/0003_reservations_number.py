# Generated by Django 4.1.3 on 2024-11-21 12:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reservations", "0002_reservations_is_confirmed_reservations_is_ordered"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservations",
            name="number",
            field=models.CharField(default="", max_length=20),
        ),
    ]
