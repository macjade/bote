# Generated by Django 3.2 on 2021-09-04 13:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20210904_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]