# Generated by Django 3.1.3 on 2020-11-15 23:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_controle_nps', '0005_auto_20201115_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questao',
            name='peso',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='Peso'),
        ),
    ]