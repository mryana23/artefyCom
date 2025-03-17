# models.py
from django.db import models
from django.contrib.auth.models import User

class Posts(models.Model):
    POST_TYPE_CHOICES = (
        ('general', 'General'),
        ('community', 'Community')
    )
    PRIVACY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private')
    )
    
    post_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    caption = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='general')
    community_id = models.IntegerField(null=True, blank=True)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')

    class Meta:
        db_table = 'posts'

class PostMedia(models.Model):
    media_id = models.AutoField(primary_key=True)
    post_id = models.IntegerField()
    media_type = models.CharField(max_length=10)  # 'image', 'video', or 'document'
    media_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_media'
        
class Hashtag(models.Model):
    hashtag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    usage_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hashtags'
        
class PostHashtag(models.Model):
    post_hashtag_id = models.AutoField(primary_key=True)
    post_id = models.IntegerField()
    hashtag_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_hashtags'
        unique_together = ('post_id', 'hashtag_id')
        
class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    post_id = models.IntegerField()
    user_id = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'

class PostInteractions(models.Model):
    interaction_id = models.AutoField(primary_key=True)
    post_id = models.IntegerField()
    user_id = models.IntegerField()
    like_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    shared_url = models.CharField(max_length=255, null=True, blank=True)
    shared_platform = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    class Meta:
        db_table = 'post_interactions'
        unique_together = ('post_id', 'user_id')

class ContentReports(models.Model):
    report_id = models.AutoField(primary_key=True)
    reporter_id = models.IntegerField()
    content_id = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Content_Reports'