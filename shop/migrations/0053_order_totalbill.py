# Generated by Django 5.0.1 on 2024-02-11 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0052_cuppon_min_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='totalbill',
            field=models.PositiveIntegerField(default=0),
        ),
    ]