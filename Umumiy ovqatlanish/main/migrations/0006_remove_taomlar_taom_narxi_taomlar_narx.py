# Generated by Django 5.1.7 on 2025-03-16 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_buyurtma_sana_remove_buyurtma_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taomlar',
            name='taom_narxi',
        ),
        migrations.AddField(
            model_name='taomlar',
            name='narx',
            field=models.IntegerField(blank=True, null=True, verbose_name='narx'),
        ),
    ]
