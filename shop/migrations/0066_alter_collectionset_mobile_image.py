# Generated by Django 5.0.1 on 2024-07-14 15:20

import shop.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0065_collectionset_mobile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionset',
            name='mobile_image',
            field=shop.models.ResizedImageField(blank=True, null=True, upload_to='collectionset/'),
        ),
    ]