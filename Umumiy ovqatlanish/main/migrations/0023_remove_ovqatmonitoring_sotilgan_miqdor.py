# Generated by Django 5.1.5 on 2025-03-25 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_alter_buyurtma_mijoz_delete_mijoz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ovqatmonitoring',
            name='sotilgan_miqdor',
        ),
    ]
