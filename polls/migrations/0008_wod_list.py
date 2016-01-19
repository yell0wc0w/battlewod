# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_auto_20160108_0546'),
    ]

    operations = [
        migrations.CreateModel(
            name='WOD_list',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('wod_type', models.CharField(max_length=20, default=None)),
                ('description', models.TextField()),
                ('date', models.DateField()),
            ],
        ),
    ]
