import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GroupChat  
from django.utils.timezone import now

class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_sender_name(self, sender_id):
        from users.models import User  # Import your User model
        try:
            user = User.objects.get(id=sender_id)
            return user.username
        except User.DoesNotExist:
            return "Unknown User"

    async def connect(self):
        self.community_id = self.scope['url_route']['kwargs']['community_id']
        self.group_name = f'chat_{self.community_id}'
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def save_message(self, message_data):
        try:
            return GroupChat.objects.create(
                community_id=self.community_id,
                message=message_data['message'],
                sender_id=message_data['sender_id'],
                sent_at=now()
            )
        except Exception as e:
            print(f"Error saving message: {str(e)}")
            raise  # Re-raise exception untuk ditangkap di receive()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            # Save to database
            chat = await self.save_message(data)
            
            # Get sender details
            sender = await self.get_sender_details(data['sender_id'])
            
            # Format message consistent with API response
            message_data = {
                'id': chat.id,
                'message': data['message'],
                'sent_at': chat.sent_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
                'sender_id': data['sender_id'],
                'sender_name': sender['username']
            }
            
            # Broadcast to group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
        except Exception as e:
            print(f"Error in receive: {str(e)}")
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    @database_sync_to_async
    def get_sender_details(self, sender_id):
        from users.models import User
        try:
            user = User.objects.get(id=sender_id)
            return {
                'username': user.username,
                'id': user.id
            }
        except User.DoesNotExist:
            return {
                'username': 'Unknown User',
                'id': sender_id
            }