# Generated by Django 2.1.2 on 2018-10-24 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_settings_twittermember'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='value',
            field=models.CharField(max_length=255, null=True),
        ),
    ]