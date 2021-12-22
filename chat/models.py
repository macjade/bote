from django.db import models
from account.models import Bote, UserProfile
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

import uuid

class Conversation(models.Model):
    CONVERSATION_TYPE_CHOICE = {
        ('individual', 'individual'),
        ('group', 'group'),
    }

    user_one = models.ForeignKey(UserProfile, related_name="chat_owner", on_delete=models.SET_NULL, null=True)
    user_two = models.ForeignKey(UserProfile, related_name="chat_visitor", on_delete=models.SET_NULL, null=True)
    room_id = models.CharField(max_length=255, default='')
    conversation_type = models.CharField(max_length=20, default='individual', choices=CONVERSATION_TYPE_CHOICE)
    timestamp = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user_one.user.get_short_name()} - {self.user_two.user.get_short_name()}"

    def generate_room_id(self):
        new_id = uuid.uuid4()
        if self.__class__.objects.filter(room_id=new_id).exists():
            return self.generate_room_id()
        else:
            return new_id

    def addconversation(self, user_one, user_two, roomId, conversation_type='individual'):

        newconvo = self
        newconvo.user_one = user_one
        newconvo.user_two = user_two
        newconvo.room_id = roomId#self.generate_room_id()
        newconvo.conversation_type = conversation_type
        newconvo.save()

        return newconvo

class Messages(models.Model):

    MESSAGE_TYPE_CHOICE = {
        ('text', 'text'),
        ('audio', 'audio'),
        ('image', 'image'),
        ('video', 'video'),
        ('document', 'document'),
    }

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    message = models.TextField(default='')
    message_type = models.CharField(default='text', max_length=20, choices=MESSAGE_TYPE_CHOICE)
    deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    receiver_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.conversation} - {self.message}"

    def addmessage(self, conversation_id, sender, message, message_type):

        newmessage = self
        newmessage.conversation = conversation_id
        newmessage.sender = sender
        newmessage.message = message
        newmessage.message_type = message_type
        newmessage.save()

        newmessage.conversation.updated_at = timezone.now()
        newmessage.conversation.save()

        return newmessage

    def has_read(self):
        self.receiver_read = True
        self.save()
        return True

class MessageFiles(models.Model):

    message = models.ForeignKey(Messages, on_delete=models.CASCADE)
    file_url = models.URLField(default='', null=True, blank=True)

    def __str__(self):
        return f"{self.message} | {self.file_url}"