# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('tag', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='AdsObject',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Initiative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'get_full_name', editable=False)),
                ('brand_id', models.PositiveIntegerField()),
                ('brand_name', models.CharField(max_length=255)),
                ('conversion_name', models.CharField(max_length=32)),
                ('actions', models.ManyToManyField(related_name='initiative_actions', to='socodri.Action')),
                ('adaccount', models.ForeignKey(related_name='initiative_adaccounts', to='socodri.AdsObject')),
                ('campaigns', models.ManyToManyField(related_name='initiative_campaigns', to='socodri.AdsObject')),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=32)),
                ('text', models.CharField(max_length=255)),
                ('object_type', models.CharField(max_length=32)),
                ('object_id', models.CharField(max_length=32)),
                ('platform', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('hash_id', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('view_window', models.CharField(max_length=32, null=True)),
                ('view_multiplier', models.FloatField(default=1.0)),
                ('click_window', models.CharField(max_length=32, null=True)),
                ('click_multiplier', models.FloatField(default=1.0)),
                ('action_total_type', models.CharField(default=b'total_actions', max_length=32)),
                ('revenue_source', models.CharField(max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('number', models.PositiveIntegerField()),
                ('actions', models.ManyToManyField(to='socodri.Action')),
            ],
        ),
        migrations.CreateModel(
            name='Window',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'name', editable=False)),
                ('view_window', models.CharField(max_length=32, null=True)),
                ('view_multiplier', models.FloatField(default=1.0)),
                ('click_window', models.CharField(max_length=32, null=True)),
                ('click_multiplier', models.FloatField(default=1.0)),
                ('action_total_type', models.CharField(default=b'total_actions', max_length=32)),
                ('revenue_source', models.CharField(default=b'Facebook', max_length=32)),
                ('label_fn', models.CharField(max_length=32, null=True)),
                ('adaccount', models.ForeignKey(related_name='window', to='socodri.AdsObject')),
                ('campaigns', models.ManyToManyField(related_name='windows', to='socodri.AdsObject')),
                ('initiative', models.ForeignKey(related_name='windows', to='socodri.Initiative', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='stage',
            name='window',
            field=models.ForeignKey(to='socodri.Window'),
        ),
        migrations.AddField(
            model_name='label',
            name='window',
            field=models.ForeignKey(related_name='labels', to='socodri.Window'),
        ),
        migrations.AddField(
            model_name='initiative',
            name='settings',
            field=models.ForeignKey(to='socodri.Settings'),
        ),
        migrations.AddField(
            model_name='action',
            name='pixel',
            field=models.ForeignKey(to='socodri.AdsObject'),
        ),
        migrations.AlterUniqueTogether(
            name='initiative',
            unique_together=set([('brand_id', 'name')]),
        ),
    ]
