# Generated by Django 2.2 on 2019-05-05 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tryactivity',
            name='UpdateTime',
            field=models.FloatField(default=1557067259.514781),
        ),
    ]