# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-27 23:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_permisos_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ventadetalle',
            name='tipo_apuesta',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
