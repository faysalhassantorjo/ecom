# Generated by Django 5.0.1 on 2024-01-21 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_order_created_at_userprofile_join_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
