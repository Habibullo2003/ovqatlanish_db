# Generated by Django 5.2 on 2025-05-14 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_buyurtma_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyurtma',
            name='additional_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
