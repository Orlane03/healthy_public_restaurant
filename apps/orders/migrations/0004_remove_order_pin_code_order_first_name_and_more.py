# Generated by Django 4.1.3 on 2024-10-28 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_remove_order_country_remove_order_first_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='pin_code',
        ),
        migrations.AddField(
            model_name='order',
            name='first_name',
            field=models.CharField(default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(default='', max_length=50, null=True),
        ),
    ]
