# posts/serializers.py
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ContentReports, Posts, PostMedia, Comments, PostInteractions
from django.db import connection 
from django.contrib.auth import get_user_model
from django.db.models import Sum
User = get_user_model()

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['media_id', 'post_id', 'file', 'media_type', 'created_at']
    def get_url(self, obj):
        request = self.context.get('request')
        if request and obj.media_url:
            return request.build_absolute_uri(settings.MEDIA_URL + obj.media_url)
        return None

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ['comment_id', 'post_id', 'user_id', 'comment', 'created_at', 'username']
        read_only_fields = ['user_id']

    def get_username(self, obj):
        user = User.objects.filter(id=obj.user_id).first()
        return user.username if user else None
    
class PostSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    share_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    hashtags = serializers.SerializerMethodField()
    
    class Meta:
        model = Posts
        fields = ['post_id', 'user_id', 'caption', 'created_at', 'media',
                'username', 'like_count', 'share_count', 'is_liked', 'comments', 'hashtags']
        read_only_fields = ['user_id']
    
    def get_media(self, obj):
        media = PostMedia.objects.filter(post_id=obj.post_id).order_by('created_at')
        return PostMediaSerializer(
            media, 
            many=True,
            context={'request': self.context.get('request')}
        ).data
    
    def get_username(self, obj):
        user = User.objects.filter(id=obj.user_id).first()
        return user.username if user else None
    
    def get_like_count(self, obj):
        # Count unique users who liked the post
        return PostInteractions.objects.filter(
            post_id=obj.post_id,
            like_count__gt=0
        ).count()
    
    def get_share_count(self, obj):
        # Count total shares across all platforms
        return PostInteractions.objects.filter(
            post_id=obj.post_id,
            share_count__gt=0
        ).count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostInteractions.objects.filter(
                post_id=obj.post_id,
                user_id=request.user.id,
                like_count__gt=0
            ).exists()
        return False
    
    def get_comments(self, obj):
        comments = Comments.objects.raw('''
            SELECT c.*, u.username 
            FROM comments c
            LEFT JOIN users.user u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
        ''', [obj.post_id])
        return CommentSerializer(comments, many=True).data
    
    def get_hashtags(self, obj):
        # Get hashtags using raw SQL query
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT h.hashtag_id, h.name, h.usage_count
                FROM hashtags h
                JOIN post_hashtags ph ON h.hashtag_id = ph.hashtag_id
                WHERE ph.post_id = %s
                ORDER BY h.name
            ''', [obj.post_id])
            columns = [col[0] for col in cursor.description]
            hashtags = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return hashtags
    
class ContentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentReports
        fields = ['report_id', 'reporter_id', 'content_id', 'reason', 'status', 'created_at']
        read_only_fields = ['report_id', 'reporter_id', 'status', 'created_at']