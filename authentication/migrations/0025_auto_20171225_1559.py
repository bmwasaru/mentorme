# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-12-25 12:59
from __future__ import unicode_literals

from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0024_auto_20171225_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=imagekit.models.fields.ProcessedImageField(upload_to='profiles'),
        ),
    ]