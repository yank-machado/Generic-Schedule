from ninja_extra import api_controller, route
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from ninja_extra.pagination import PaginatedResponseSchema, PageNumberPaginationExtra, paginate
from ninja_extra.searching import Searching
from ninja_extra.searching import searching
from typing import List

from company.models import Company
from slot.models import Slot
from slot.schema import (
    SlotIn, SlotOut, SlotFilter
)


@api_controller('/slots', tags=['Slots'])
class SlotController:
    
    @property
    def slot_filters(self):
        return SlotFilter
    
    @route.get('/', response=PaginatedResponseSchema[SlotOut])
    @paginate(PageNumberPaginationExtra)
    @searching(Searching)
    def list_slots(self, search_fields=None, **kwargs):
        queryset = Slot.objects.all()
        
        filters = self.slot_filters(**kwargs) if kwargs else None
        
        if filters:
            if filters.company_id:
                queryset = queryset.filter(company_id=filters.company_id)
            
            if filters.start_date:
                queryset = queryset.filter(start_time__gte=filters.start_date)
            
            if filters.end_date:
                queryset = queryset.filter(end_time__lte=filters.end_date)
            
            if filters.only_available:
                queryset = queryset.filter(is_available=True)
        
        return queryset
    
    @route.post('/', response={201: SlotOut})
    def create_slot(self, payload: SlotIn, company_id: int):
        company = get_object_or_404(Company, id=company_id)
        
        # Verificar sobreposição de slots
        overlapping_slots = Slot.objects.filter(
            company=company,
            start_time__lt=payload.end_time,
            end_time__gt=payload.start_time
        )
        
        if overlapping_slots.exists():
            return 400, {"detail": "Este slot se sobrepõe a outro slot existente"}
        
        slot = Slot.objects.create(
            company=company,
            start_time=payload.start_time,
            end_time=payload.end_time,
            is_available=True
        )
        return 201, slot
    
    @route.get('/{slot_id}', response=SlotOut)
    def get_slot(self, slot_id: int):
        return get_object_or_404(Slot, id=slot_id)
    
    @route.put('/{slot_id}', response=SlotOut)
    def update_slot(self, slot_id: int, payload: SlotIn):
        slot = get_object_or_404(Slot, id=slot_id)
        
        # Verificar sobreposição de slots (excluindo o próprio slot)
        overlapping_slots = Slot.objects.filter(
            company=slot.company,
            start_time__lt=payload.end_time,
            end_time__gt=payload.start_time
        ).exclude(id=slot_id)
        
        if overlapping_slots.exists():
            return 400, {"detail": "Este slot se sobrepõe a outro slot existente"}
        
        slot.start_time = payload.start_time
        slot.end_time = payload.end_time
        slot.save()
        return slot
    
    @route.delete('/{slot_id}', response={204: None})
    def delete_slot(self, slot_id: int):
        slot = get_object_or_404(Slot, id=slot_id)
        
        # Verificar se há agendamentos para este slot
        if slot.bookings.exists():
            return 400, {"detail": "Não é possível excluir um slot com agendamentos"}
        
        slot.delete()
        return 204, None
    
    @route.post('/bulk-create', response={201: List[SlotOut]})
    def bulk_create_slots(self, company_id: int, start_date: datetime, end_date: datetime, 
                          duration_minutes: int = 60, start_hour: int = 8, end_hour: int = 18,
                          days_of_week: List[int] = [0, 1, 2, 3, 4, 5, 6]):  # 0=Segunda, 6=Domingo
        """Criar múltiplos slots para uma empresa com intervalo regular"""
        company = get_object_or_404(Company, id=company_id)
        created_slots = []
        
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        while current_date <= end_date:
            # Verificar se o dia da semana está incluído
            if current_date.weekday() in days_of_week:
                # Criar slots para este dia
                slot_start = current_date.replace(hour=start_hour, minute=0)
                
                while slot_start.hour < end_hour:
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    # Verificar sobreposição
                    overlapping = Slot.objects.filter(
                        company=company,
                        start_time__lt=slot_end,
                        end_time__gt=slot_start
                    ).exists()
                    
                    if not overlapping:
                        slot = Slot.objects.create(
                            company=company,
                            start_time=slot_start,
                            end_time=slot_end,
                            is_available=True
                        )
                        created_slots.append(slot)
                    
                    # Avançar para o próximo slot
                    slot_start = slot_end
            
            # Avançar para o próximo dia
            current_date += timedelta(days=1)
        
        return 201, created_slots