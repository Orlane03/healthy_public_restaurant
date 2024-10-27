# Generated by Django 4.1.3 on 2024-10-27 02:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_confirmed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="order",
            name="tax_data",
            field=models.JSONField(
                blank=True,
                help_text="Data format: {'tax_type':{'tax_percentage':'tax_amount'}}",
                null=True,
            ),
        ),
    ]