from ninja_extra import api_controller, route
from django.shortcuts import get_object_or_404
from typing import Optional
from datetime import timedelta
from ninja_extra.pagination import PaginatedResponseSchema, PageNumberPaginationExtra, paginate
from ninja_extra.searching import Searching
from ninja_extra.searching import searching

from company.models import Company
from servicetype.models import ServiceType
from servicetype.schema import (
    ServiceTypeIn, ServiceTypeOut,

)


@api_controller('/service-types', tags=['Service Types'])
class ServiceTypeController:
    
    @route.get('/', response=PaginatedResponseSchema[ServiceTypeOut])
    @paginate(PageNumberPaginationExtra)
    @searching(Searching)
    def list_service_types(self, company_id: Optional[int] = None):
        queryset = ServiceType.objects.filter(company_id=company_id) if company_id else ServiceType.objects.all()
        return queryset  
    
    @route.post('/', response={201: ServiceTypeOut})
    def create_service_type(self, payload: ServiceTypeIn, company_id: int):
        company = get_object_or_404(Company, id=company_id)
        service_type = ServiceType.objects.create(
            company=company,
            name=payload.name,
            description=payload.description,
            duration=timedelta(minutes=payload.duration_minutes),  # Converte minutos para timedelta
            price=payload.price
        )
        return 201, service_type
    

    @route.get('/{service_type_id}', response=ServiceTypeOut)
    def get_service_type(self, service_type_id: int):
        return get_object_or_404(ServiceType, id=service_type_id)
    
    @route.put('/{service_type_id}', response=ServiceTypeOut)
    def update_service_type(self, service_type_id: int, payload: ServiceTypeIn):
        service_type = get_object_or_404(ServiceType, id=service_type_id)
        service_type.name = payload.name
        service_type.description = payload.description
        service_type.duration = timedelta(minutes=payload.duration_minutes)
        service_type.price = payload.price
        service_type.save()
        return {
            **service_type.__dict__,
            'duration_minutes': int(service_type.duration.total_seconds() / 60)
        }
    
    @route.delete('/{service_type_id}', response={204: None})
    def delete_service_type(self, service_type_id: int):
        service_type = get_object_or_404(ServiceType, id=service_type_id)
        service_type.delete()
        return 204, None