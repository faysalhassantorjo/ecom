# Generated by Django 5.0.1 on 2024-11-08 15:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0080_shippingaddress_seen_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='seen_by',
            field=models.ManyToManyField(blank=True, related_name='seen_orders', to=settings.AUTH_USER_MODEL),
        ),
    ]
