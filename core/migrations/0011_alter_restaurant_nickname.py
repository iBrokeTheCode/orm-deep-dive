# Generated by Django 5.2 on 2025-04-15 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_restaurant_restaurant_name_unique_insensitive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='nickname',
            field=models.CharField(default='', max_length=100),
        ),
    ]
