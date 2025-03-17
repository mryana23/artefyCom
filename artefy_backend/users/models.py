# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User'),
    )
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email