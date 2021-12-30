# Generated by Django 3.2 on 2021-12-30 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='user_one',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chat_owner', to='account.userprofile'),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='user_two',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chat_visitor', to='account.userprofile'),
        ),
        migrations.AlterField(
            model_name='messages',
            name='message_type',
            field=models.CharField(choices=[('video', 'video'), ('document', 'document'), ('image', 'image'), ('text', 'text'), ('audio', 'audio')], default='text', max_length=20),
        ),
    ]
