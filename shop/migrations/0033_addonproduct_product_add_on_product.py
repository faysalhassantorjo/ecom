# Generated by Django 5.0.1 on 2024-02-09 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0032_product_discount_product_discount_percent_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddOnProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='add_on_product',
            field=models.ManyToManyField(to='shop.addonproduct'),
        ),
    ]
