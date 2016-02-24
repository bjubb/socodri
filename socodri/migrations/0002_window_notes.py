# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socodri', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='window',
            name='notes',
            field=models.TextField(null=True),
        ),
    ]
