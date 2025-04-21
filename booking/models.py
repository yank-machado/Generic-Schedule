from django.db import models
from django.core.exceptions import ValidationError
from slot.models import Slot
from client.models import Client
from servicetype.models import ServiceType



class Booking(models.Model):
    """Agendamento de serviço"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
        ('completed', 'Concluído'),
    ]
    
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='bookings')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def clean(self):

        if not self.slot.is_available and self.pk is None:
            raise ValidationError('Este slot não está disponível.')
        

        if self.service_type.company != self.slot.company:
            raise ValidationError('O serviço deve pertencer à mesma empresa do slot.')
        

        slot_duration = self.slot.end_time - self.slot.start_time
        if self.service_type.duration > slot_duration:
            raise ValidationError('A duração do serviço excede o tempo disponível no slot.')
    
    def save(self, *args, **kwargs):
        self.clean()
        

        if self.status in ['confirmed', 'completed'] and self.slot.is_available:
            self.slot.is_available = False
            self.slot.save()
        

        if self.status == 'cancelled' and not self.slot.is_available:
            self.slot.is_available = True
            self.slot.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.service_type.name} - {self.client.name} - {self.slot.start_time.strftime('%d/%m/%Y %H:%M')}"
