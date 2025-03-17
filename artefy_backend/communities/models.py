from django.db import models
class Community(models.Model):
    STATUS_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private')
    )
    TYPE_CHOICES = (
        ('free', 'Free'),
        ('premium', 'Premium')
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category_id = models.IntegerField()
    communities_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='public')
    rules = models.TextField(null=True, blank=True)
    subscription_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    photo_community = models.ImageField(upload_to='community_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Communities'

class CommunityMember(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member')
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned')
    )
    
    community_id = models.IntegerField()
    user_id = models.IntegerField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Community_Members'
        unique_together = ('community_id', 'user_id')

class CommunityJoinRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    
    community_id = models.IntegerField()
    user_id = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_message = models.TextField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'Community_Join_Requests'
        unique_together = ('community_id', 'user_id')