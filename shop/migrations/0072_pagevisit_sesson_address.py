# Generated by Django 5.0.1 on 2024-09-02 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0071_pagevisit'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagevisit',
            name='sesson_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
