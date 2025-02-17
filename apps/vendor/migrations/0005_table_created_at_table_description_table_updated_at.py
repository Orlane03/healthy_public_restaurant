# Generated by Django 4.1.3 on 2024-11-11 07:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("vendor", "0004_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="table",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="table",
            name="description",
            field=models.TextField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name="table",
            name="updated_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
