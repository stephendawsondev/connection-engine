# Generated by Django 5.1.7 on 2025-03-23 21:37

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0003_merge_20250323_0030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]
