# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-27 21:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hk-db', '0001_initial')
    ]

    operations = [
        migrations.DeleteModel('Greeting'),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(editable=True, verbose_name=b'Location')),
            ],
        ),
    ]
