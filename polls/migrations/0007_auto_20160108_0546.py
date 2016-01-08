# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_auto_20151222_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='athleteprofile',
            name='cumulative_reads',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='athleteprofile',
            name='cumulative_writes',
            field=models.IntegerField(default=0),
        ),
    ]
