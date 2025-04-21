from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    """Empresa/prestador de serviços"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name