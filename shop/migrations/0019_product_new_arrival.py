# Generated by Django 5.0.1 on 2024-01-22 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0018_rename_ariive_at_product_arrive_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='new_arrival',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
