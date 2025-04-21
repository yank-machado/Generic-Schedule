from ninja import Schema
from typing import Optional
from decimal import Decimal
from datetime import timedelta


class ServiceTypeIn(Schema):
    name: str
    description: Optional[str] = None
    duration_minutes: int   
    price: Decimal = Decimal('0.00')


class ServiceTypeOut(Schema):
    id: int
    name: str
    description: Optional[str]
    duration_minutes: int  # Já em minutos (não precisa converter no controller)
    duration_formatted: str  # Formato "HH:MM:SS"
    price: Decimal
    company_id: int
    
    @staticmethod
    def resolve_duration_formatted(obj):
        """Converte duration_minutes para o formato HH:MM:SS"""
        duration_minutes = obj.get('duration_minutes') if isinstance(obj, dict) else int(obj.duration.total_seconds() / 60)
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        return f"{hours:02d}:{minutes:02d}:00"  # Segundos sempre 00