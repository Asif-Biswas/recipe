from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.

ACCOUNT_TYPE = (
    ('rapper', 'Rapper'),
    ('organizer', 'Organizer'),
    ('user', 'User'),
    ('admin', 'Admin')
)

class UserProfile(models.Model):
    """
    This is a table for storing user profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True)
    bio = models.TextField(blank=True)
    other_details = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OTPVerification(models.Model):
    """
    This is a table for storing OTP verification.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
