from django.db import models
from datetime import timedelta
from company.models import Company


class ServiceType(models.Model):
    """Tipo de serviço oferecido"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration = models.DurationField(default=timedelta(hours=1))  # Duração padrão de 1 hora
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='service_types')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.name} ({self.company.name})"
        
    @property
    def duration_minutes(self):
        """Retorna a duração em minutos"""
        return int(self.duration.total_seconds() / 60)