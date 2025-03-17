# chat/models.py
from django.db import models
from django.utils import timezone

class GroupChat(models.Model):
    community_id = models.IntegerField()
    message = models.TextField()
    sender_id = models.IntegerField()
    sent_at = models.DateTimeField(auto_now_add=True) 
    status = models.CharField(max_length=10, default='unread')

    class Meta:
        db_table = 'group_chats'