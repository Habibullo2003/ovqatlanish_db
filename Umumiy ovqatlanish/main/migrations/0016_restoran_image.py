# Generated by Django 4.2.20 on 2025-03-20 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_remove_restoran_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='restoran',
            name='image',
            field=models.ImageField(blank=True, default='images/panoramic.jpg', null=True, upload_to='images/', verbose_name='image'),
        ),
    ]
