# Generated by Django 3.2 on 2021-09-04 13:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 4, 13, 24, 59, 968543, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='conversation_type',
            field=models.CharField(choices=[('group', 'group'), ('individual', 'individual')], default='individual', max_length=20),
        ),
        migrations.AlterField(
            model_name='messages',
            name='message_type',
            field=models.CharField(choices=[('audio', 'audio'), ('image', 'image'), ('text', 'text'), ('document', 'document'), ('video', 'video')], default='text', max_length=20),
        ),
    ]
