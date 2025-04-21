from ninja_extra import api_controller, route
from django.shortcuts import get_object_or_404
from booking.models import Booking, Slot, ServiceType, Client
from ninja_extra.pagination import PaginatedResponseSchema, PageNumberPaginationExtra, paginate
from ninja_extra.searching import searching
from booking.schema import BookingOut, BookingFilter, BookingIn



@api_controller('/bookings', tags=['Bookings'])
class BookingController:
    
    @property
    def booking_filters(self):
        return BookingFilter
    
    @route.get('/', response=PaginatedResponseSchema[BookingOut])
    @paginate(PageNumberPaginationExtra)
    @searching
    def list_bookings(self, search_fields=None, **kwargs):
        queryset = Booking.objects.all()
        
        filters = self.booking_filters(**kwargs) if kwargs else None
        
        if filters:
            if filters.company_id:
                queryset = queryset.filter(slot__company_id=filters.company_id)
            
            if filters.client_id:
                queryset = queryset.filter(client_id=filters.client_id)
            
            if filters.status:
                queryset = queryset.filter(status=filters.status)
            
            if filters.start_date:
                queryset = queryset.filter(slot__start_time__gte=filters.start_date)
            
            if filters.end_date:
                queryset = queryset.filter(slot__end_time__lte=filters.end_date)
        
        return queryset
    
    @route.post('/', response={201: BookingOut})
    def create_booking(self, payload: BookingIn, client_id: int):
        slot = get_object_or_404(Slot, id=payload.slot_id)
        service_type = get_object_or_404(ServiceType, id=payload.service_type_id)
        client = get_object_or_404(Client, id=client_id)
        

        if not slot.is_available:
            return 400, {"detail": "Este slot não está disponível"}
        

        if service_type.company != slot.company:
            return 400, {"detail": "O serviço deve pertencer à mesma empresa do slot"}
        

        slot_duration = slot.end_time - slot.start_time
        if service_type.duration > slot_duration:
            return 400, {"detail": "A duração do serviço excede o tempo disponível no slot"}
        

        booking = Booking.objects.create(
            slot=slot,
            service_type=service_type,
            client=client,
            status='confirmed', 
            notes=payload.notes
        )
        
        slot.is_available = False
        slot.save()
        
        return 201, booking
    
    @route.get('/{booking_id}', response=BookingOut)
    def get_booking(self, booking_id: int):
        return get_object_or_404(Booking, id=booking_id)
    
    @route.patch('/{booking_id}/status', response=BookingOut)
    def update_booking_status(self, booking_id: int, status: str):
        booking = get_object_or_404(Booking, id=booking_id)
        
        if status not in [status_choice[0] for status_choice in Booking.STATUS_CHOICES]:
            return 400, {"detail": "Status inválido"}
        
        old_status = booking.status
        booking.status = status
        booking.save()
        
        if old_status != 'cancelled' and status == 'cancelled':
            booking.slot.is_available = True
            booking.slot.save()
        elif old_status == 'cancelled' and status != 'cancelled':
            booking.slot.is_available = False
            booking.slot.save()
        
        return booking
    
    @route.delete('/{booking_id}', response={204: None})
    def delete_booking(self, booking_id: int):
        booking = get_object_or_404(Booking, id=booking_id)
        
        slot = booking.slot
        slot.is_available = True
        slot.save()
        
        booking.delete()
        return 204, None