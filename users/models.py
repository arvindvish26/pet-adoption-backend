from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='admins/', blank=True, null=True)
    is_superadmin = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username} (Superadmin: {self.is_superadmin})"
