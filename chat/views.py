from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from django.db.models import Q

from .models import Conversation, Messages, MessageFiles
from account.models import UserProfile, Bote

import cloudinary
import cloudinary.uploader
import cloudinary.api

channel_layer = get_channel_layer()

class ChatConversations(APIView):

    def get(self, request):
        data = request.GET
        auth_user = request.user.email
        get_user = request.user.userprofile_set.get()

        get_conversations = Conversation.objects.filter(Q(user_one=get_user.pk) | Q(user_two=get_user.pk))

        conversation = []
        for i in get_conversations:
            msg_unread = i.messages_set.exclude(sender=get_user.pk).filter(receiver_read=False).count()
            user = i.user_one if i.user_one.user.email != auth_user else i.user_two
            conversation.append({
                "id": i.pk,
                "name": user.user.username,
                "room_id": i.room_id,
                "status": "online" if user.is_connected else "offline",
                "unread": msg_unread,
                "profile_image": user.profile_picture
            })

        return Response(conversation)

class ConversationMessage(APIView):

    def uploadimageanddocument(self, file_type, file):
        if file_type == 'image':
            upload_result = cloudinary.uploader.upload(file, folder='bote/images')
        elif file_type == 'video':
            upload_result = cloudinary.uploader.upload(file, folder='bote/videos')
        else:
            upload_result = cloudinary.uploader.upload(file, folder='bote/files')

        return upload_result['secure_url']

    def get(self, request, **kwargs):
        data = request.GET
        roomId = kwargs.get('room')
        auth_user = request.user
        get_conversations = Conversation.objects.filter(room_id=roomId)
        context={}
        messages = []
        if (get_conversations):
            for i in get_conversations[0].messages_set.all():
                media={}
                if i.messagefiles_set.filter():
                    media["url"] = i.messagefiles_set.get().file_url

                messages.append({
                    "id": i.pk,
                    "message": i.message,
                    "owner": str(i.sender.user.username) if i.sender.user.email != auth_user.email else 'me',
                    "type": i.message_type,
                    "datetime": str(i.timestamp),
                    "media": media
                })
            context["status"]=True
            context["message"]=messages
        else:
            context["status"]=False


        return Response(context)

    def post(self, request, **kwargs):
        data = request.data
        roomId = kwargs.get('room')
        auth_user = request.user
        receiving_user = data.get('receipt_user', None)
        message = data.get('message', '')
        message_type = data['type']
        media = data.get('media', None)
        context = {}

        get_conversations = Conversation.objects.filter(room_id=roomId).exists()

        convo_obj = None

        if not get_conversations:
            user_one = request.user.userprofile_set.get()
            if receiving_user:
                user_two = Bote.objects.filter(username=receiving_user)
                if user_two:
                    user_two = user_two[0].userprofile_set.get()
                    convo_obj = Conversation().addconversation(user_one, user_two, roomId)
                else:
                    return Response({
                        'status': False,
                        'message': "User doesn't exists"
                    })
            else:
                return Response({
                    'status': False,
                    'message': "Message must have a receiving user"
                })

        convo_obj = convo_obj if convo_obj else Conversation.objects.get(room_id=roomId)
        sender = auth_user.userprofile_set.get()
        newmessage = Messages().addmessage(convo_obj, sender, message, message_type)

        if media:
            newmessage.messagefiles_set.create(
                file_url=self.uploadimageanddocument(message_type, media)
            )
        media_dict = {}
        if newmessage.messagefiles_set.filter():
            media_dict["url"] = newmessage.messagefiles_set.get().file_url

        sending_msg = {
            "id": newmessage.pk,
            "message": newmessage.message,
            "owner": str(newmessage.sender.user.username),
            "type": newmessage.message_type,
            "datetime": str(newmessage.timestamp),
            "media": media_dict
        }

        group_name = f"conversation_{roomId}"
        async_to_sync(channel_layer.group_send)(group_name, {'type': "sendmessage", "text": sending_msg})

        context["status"] = True
        context["message"] = "message sent"

        return Response(context)

class ReadMessage(APIView):


    def post(self, request):
        context = {}
        data = request.data
        convo_id = data['id']
        auth_user = request.user
        get_auth = auth_user.userprofile_set.get()
        get_conversations = Conversation.objects.get(pk=int(convo_id))

        for i in get_conversations.messages_set.exclude(sender=get_auth.pk).filter(receiver_read=False):
            i.has_read()

        context['status'] = True
        return Response(context)

class GetNewChatList(APIView):


    def get(self, request):
        data = request.GET
        auth_user = request.user
        user_filter = data.get('user', '')
        users_dict = {}
        users_list = []

        get_chat_list = Bote.objects.filter(user=True, username__icontains=user_filter).exclude(pk=auth_user.pk).order_by('username')
        d_auth_user = auth_user.userprofile_set.get().pk
        for i in get_chat_list:
            user_profile = i.userprofile_set.get().pk

            if not Conversation.objects.filter(Q(user_one=d_auth_user) | Q(user_two=d_auth_user)).filter(Q(user_one=user_profile) | Q(user_two=user_profile)).exists():

                if not str(i.username)[0].upper() in users_dict.keys():
                    users_dict[str(i.username)[0].upper()] = []

                users_dict[str(i.username)[0].upper()].append({
                    'id': f"new_chat_{i.pk}",
                    'name': i.username,
                    "room_id": str(Conversation().generate_room_id()),
                    "status": "online" if i.userprofile_set.get().is_connected else "offline",
                    "unread": 0,
                    "profile_image": i.userprofile_set.get().profile_picture
                })

        for j in users_dict.keys():
            users_list.append({
                "divider": str(j),
                "list_items": users_dict[j]
            })


        return Response({"status": True, "data_list": users_list})

class ClearChatView(APIView):

    def post(self, request):
        data = request.data
        auth_user = request.user
        roomId = data["room"]
        context = {}

        if not auth_user.is_authenticated:
            context["status"] = False
            context["message"] = "User not found"
            return Response(context)

        get_conversations = Conversation.objects.filter(room_id=roomId)

        if get_conversations:
            get_conversations[0].messages_set.all().delete()
            context["status"]= True
        else:
            context["status"] = False
            context["message"] = "Unable to delete messages"

        return Response(context)
