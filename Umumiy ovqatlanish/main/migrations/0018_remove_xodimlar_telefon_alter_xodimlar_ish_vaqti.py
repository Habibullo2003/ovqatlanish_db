# Generated by Django 4.2.20 on 2025-03-20 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_xodimlar_ish_vaqti_alter_restoran_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='xodimlar',
            name='telefon',
        ),
        migrations.AlterField(
            model_name='xodimlar',
            name='ish_vaqti',
            field=models.CharField(max_length=100, verbose_name='ish vaqti'),
        ),
    ]
