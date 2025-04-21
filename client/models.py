from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    """Cliente que agenda serviços"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.name