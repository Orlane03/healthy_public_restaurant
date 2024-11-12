# Generated by Django 4.1.3 on 2024-11-11 07:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vendor", "0006_remove_table_max_people_remove_table_min_people"),
    ]

    operations = [
        migrations.AddField(
            model_name="table",
            name="number",
            field=models.CharField(default="", max_length=200),
        ),
        migrations.AlterField(
            model_name="table",
            name="description",
            field=models.TextField(blank=True, max_length=250, null=True),
        ),
    ]
