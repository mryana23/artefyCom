# chat/views.py
import json
from django.http import JsonResponse
from django.db import connection
from .models import GroupChat
from users.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.decorators import login_required
@csrf_exempt
def get_group_messages(request, community_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    gc.id,
                    gc.message,
                    gc.sent_at,
                    gc.sender_id,
                    u.username as sender_name
                FROM group_chats gc
                LEFT JOIN users_user u ON gc.sender_id = u.id
                WHERE gc.community_id = %s
                ORDER BY gc.sent_at ASC
                LIMIT 50
            """, [community_id])
            
            messages = [{
                'id': row[0],
                'message': row[1],
                'sent_at': row[2].strftime('%Y-%m-%d %H:%M:%S.%f'),
                'sender_id': row[3],
                'sender_name': row[4] or 'Unknown User'
            } for row in cursor.fetchall()]
            
        return JsonResponse({
            'messages': messages
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, community_id):
    try:
        data = json.loads(request.body)
        message = data.get('message')
        sender_id = request.user.id  # Ambil ID dari user yang terautentikasi
        
        new_message = GroupChat.objects.create(
            community_id=community_id,
            message=message,
            sender_id=sender_id
        )
        
        return JsonResponse({
            'message': 'Message sent successfully',
            'message_id': new_message.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)