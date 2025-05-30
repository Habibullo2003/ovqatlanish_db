# Generated by Django 5.2 on 2025-05-14 16:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_kuryer_created_at_kuryer_rating_alter_kuryer_band_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kuryer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='kuryer',
            name='rating',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)]),
        ),
    ]
