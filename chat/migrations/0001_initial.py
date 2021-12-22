# Generated by Django 3.2 on 2021-09-04 12:00

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conversation_type', models.CharField(choices=[('individual', 'individual'), ('group', 'group')], default='individual', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=True)),
                ('user_one', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_owner', to='account.userprofile')),
                ('user_two', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_visitor', to='account.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(default='')),
                ('message_type', models.CharField(choices=[('audio', 'audio'), ('text', 'text'), ('video', 'video'), ('image', 'image'), ('document', 'document')], default='text', max_length=20)),
                ('deleted', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('receiver_read', models.BooleanField(default=False)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.conversation')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='MessageFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_url', models.URLField(blank=True, default='', null=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.messages')),
            ],
        ),
    ]
