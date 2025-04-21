# core/tests/test_bookings.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import datetime, timedelta
from decimal import Decimal
from core.models import Company, Client, ServiceType, Slot, Booking, User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def company():
    user = User.objects.create_user(username='testcompany', password='password123')
    return Company.objects.create(user=user, name='Test Company')

@pytest.fixture
def client_user():
    user = User.objects.create_user(username='testclient', password='password123')
    return Client.objects.create(user=user, name='Test Client', phone='123456789')

@pytest.fixture
def service_type(company):
    return ServiceType.objects.create(
        company=company,
        name='Corte de Cabelo',
        duration=timedelta(minutes=45),
        price=Decimal('50.00')
    )

@pytest.fixture
def slot(company):
    start_time = datetime.now() + timedelta(days=1)
    return Slot.objects.create(
        company=company,
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        is_available=True
    )

@pytest.mark.django_db
class TestBookingAPI:
    
    def test_create_booking(self, api_client, company, client_user, service_type, slot):
        url = '/api/bookings/'
        
        payload = {
            'slot_id': slot.id,
            'service_type_id': service_type.id,
            'notes': 'Preferência por atendimento rápido',
            'client_id': client_user.id
        }
        
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 201
        assert Booking.objects.count() == 1
        
        booking = Booking.objects.first()
        assert booking.slot == slot
        assert booking.service_type == service_type
        assert booking.client == client_user
        assert booking.status == 'confirmed'
        
        # Verificar se o slot foi marcado como indisponível
        slot.refresh_from_db()
        assert not slot.is_available
    
    def test_get_booking_list(self, api_client, company, client_user, service_type, slot):
        # Criar um agendamento para testar
        booking = Booking.objects.create(
            slot=slot,
            service_type=service_type,
            client=client_user,
            status='confirmed'
        )
        
        url = '/api/bookings/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
    
    def test_filter_bookings(self, api_client, company, client_user, service_type):
        # Criar outro cliente e slots para testar filtros
        user2 = User.objects.create_user(username='otherclient', password='password123')
        other_client = Client.objects.create(user=user2, name='Other Client')
        
        start_time = datetime.now() + timedelta(days=1)
        
        # Criar 2 slots e agendamentos para o primeiro cliente
        for i in range(2):
            slot = Slot.objects.create(
                company=company,
                start_time=start_time + timedelta(hours=i*2),
                end_time=start_time + timedelta(hours=(i*2)+1)
            )
            Booking.objects.create(
                slot=slot,
                service_type=service_type,
                client=client_user,
                status='confirmed' if i == 0 else 'pending'
            )
        
        # Criar 1 slot e agendamento para o segundo cliente
        slot = Slot.objects.create(
            company=company,
            start_time=start_time + timedelta(hours=4),
            end_time=start_time + timedelta(hours=5)
        )
        Booking.objects.create(
            slot=slot,
            service_type=service_type,
            client=other_client,
            status='confirmed'
        )
        
        # Filtrar agendamentos pelo primeiro cliente
        url = f"/api/bookings/?client_id={client_user.id}"
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.data['count'] == 2
        
        # Filtrar agendamentos pelo status
        url = f"/api/bookings/?status=confirmed"
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.data['count'] == 2
    
    def test_update_booking_status(self, api_client, company, client_user, service_type, slot):
        # Criar um agendamento e depois atualizar seu status
        booking = Booking.objects.create(
            slot=slot,
            service_type=service_type,
            client=client_user,
            status='confirmed'
        )
        
        url = f"/api/bookings/{booking.id}/status"
        payload = {'status': 'cancelled'}
        
        response = api_client.patch(url, payload, format='json')
        
        assert response.status_code == 200
        booking.refresh_from_db()
        assert booking.status == 'cancelled'
        
        # Verificar se o slot foi marcado como disponível novamente
        slot.refresh_from_db()
        assert slot.is_available
    
    def test_booking_validation(self, api_client, company, client_user, service_type):
        # Testar validação quando o slot não está disponível
        start_time = datetime.now() + timedelta(days=1)
        slot = Slot.objects.create(
            company=company,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            is_available=False  # Já ocupado
        )
        
        url = reverse('api-1.0.0:bookings')
        payload = {
            'slot_id': slot.id,
            'service_type_id': service_type.id,
            'client_id': client_user.id
        }
        
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400
        assert "não está disponível" in response.data['detail']
    
    def test_booking_duration_validation(self, api_client, company, client_user):
        # Testar validação quando a duração do serviço é maior que o slot
        start_time = datetime.now() + timedelta(days=1)
        slot = Slot.objects.create(
            company=company,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=30)  # Slot de 30 minutos
        )
        
        # Criar um serviço com duração maior que o slot
        service_type = ServiceType.objects.create(
            company=company,
            name='Tratamento Completo',
            duration=timedelta(minutes=45),  # Duração de 45 minutos
            price=Decimal('80.00')
        )
        
        url = reverse('api-1.0.0:bookings')
        payload = {
            'slot_id': slot.id,
            'service_type_id': service_type.id,
            'client_id': client_user.id
        }
        
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400
        assert "excede o tempo disponível" in response.data['detail']
    
    def test_delete_booking(self, api_client, company, client_user, service_type, slot):
        # Criar um agendamento e depois deletá-lo
        booking = Booking.objects.create(
            slot=slot,
            service_type=service_type,
            client=client_user,
            status='confirmed'
        )
        
        # O slot deve estar indisponível
        slot.is_available = False
        slot.save()
        
        url = f"{reverse('api-1.0.0:bookings')}{booking.id}"
        response = api_client.delete(url)
        
        assert response.status_code == 204
        assert Booking.objects.count() == 0
        
        # Verificar se o slot foi marcado como disponível novamente
        slot.refresh_from_db()
        assert slot.is_available