from django.db import models
from django.core.exceptions import ValidationError
from company.models import Company


class Slot(models.Model):
    """Slot de horário disponível para agendamento"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['start_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='check_end_time_after_start_time'
            )
        ]
    
    def clean(self):
        # Verificar se há sobreposição de slots para a mesma empresa
        overlapping_slots = Slot.objects.filter(
            company=self.company,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if overlapping_slots.exists():
            raise ValidationError('Este slot se sobrepõe a outro slot existente.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.company.name}: {self.start_time.strftime('%d/%m/%Y %H:%M')} - {self.end_time.strftime('%H:%M')}"
