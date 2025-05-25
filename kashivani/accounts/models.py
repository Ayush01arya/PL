from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile model for additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"