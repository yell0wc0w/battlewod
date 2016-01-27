# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0008_wod_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='athleteprofile',
            name='max_handstand_push_up',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='athleteprofile',
            name='max_muscle_up',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='athleteprofile',
            name='max_pull_ups',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='athleteprofile',
            name='overhead_squat_1rm',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='athleteprofile',
            name='thruster_1rm',
            field=models.IntegerField(default=0),
        ),
    ]
