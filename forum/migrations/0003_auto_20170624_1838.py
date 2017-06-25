# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_column_img'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='column',
            options={'ordering': ['-post_number'], 'verbose_name_plural': '\u677f\u5757'},
        ),
    ]
