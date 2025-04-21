import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import timedelta
from decimal import Decimal
from core.models import Company, ServiceType, User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def company():
    user = User.objects.create_user(username='testcompany', password='password123')
    return Company.objects.create(user=user, name='Test Company')

@pytest.mark.django_db
class TestServiceTypeAPI:
    
    def test_create_service_type(self, api_client, company):
        url = '/api/service-types/'
        
        payload = {
            'name': 'Corte de Cabelo',
            'description': 'Corte profissional',
            'duration_minutes': 45,
            'price': '50.00',
            'company_id': company.id
        }
        
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 201
        assert ServiceType.objects.count() == 1
        service = ServiceType.objects.first()
        assert service.name == 'Corte de Cabelo'
        assert service.duration == timedelta(minutes=45)
        assert service.price == Decimal('50.00')
    
    def test_get_service_type_list(self, api_client, company):
        # Criar alguns tipos de serviço para testar
        ServiceType.objects.create(
            company=company,
            name='Corte de Cabelo',
            duration=timedelta(minutes=45),
            price=Decimal('50.00')
        )
        ServiceType.objects.create(
            company=company,
            name='Manicure',
            duration=timedelta(minutes=30),
            price=Decimal('35.00')
        )
        
        url = '/api/service-types/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 2
    
    def test_filter_service_types_by_company(self, api_client, company):
        # Criar outra empresa e serviços para ambas
        user2 = User.objects.create_user(username='othercompany', password='password123')
        other_company = Company.objects.create(user=user2, name='Other Company')
        
        # Criar 2 serviços para a primeira empresa
        ServiceType.objects.create(
            company=company,
            name='Corte de Cabelo',
            duration=timedelta(minutes=45),
            price=Decimal('50.00')
        )
        ServiceType.objects.create(
            company=company,
            name='Manicure',
            duration=timedelta(minutes=30),
            price=Decimal('35.00')
        )
        
        # Criar 1 serviço para a segunda empresa
        ServiceType.objects.create(
            company=other_company,
            name='Massagem',
            duration=timedelta(minutes=60),
            price=Decimal('80.00')
        )
        
        # Filtrar serviços pela primeira empresa
        url = f"/api/service-types/?company_id={company.id}"
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 2
        
        # Verificar se todos os serviços retornados são da empresa correta
        for service in response.data:
            assert service['company_id'] == company.id
    
    def test_update_service_type(self, api_client, company):
        # Criar um serviço e depois atualizá-lo
        service = ServiceType.objects.create(
            company=company,
            name='Corte de Cabelo',
            duration=timedelta(minutes=45),
            price=Decimal('50.00')
        )
        
        url = f"/api/service-types/{service.id}"
        payload = {
            'name': 'Corte de Cabelo Premium',
            'description': 'Corte profissional com produtos premium',
            'duration_minutes': 60,
            'price': '65.00'
        }
        
        response = api_client.put(url, payload, format='json')
        
        assert response.status_code == 200
        service.refresh_from_db()
        assert service.name == 'Corte de Cabelo Premium'
        assert service.description == 'Corte profissional com produtos premium'
        assert service.duration == timedelta(minutes=60)
        assert service.price == Decimal('65.00')
    
    def test_delete_service_type(self, api_client, company):
        # Criar um serviço e depois deletá-lo
        service = ServiceType.objects.create(
            company=company,
            name='Corte de Cabelo',
            duration=timedelta(minutes=45),
            price=Decimal('50.00')
        )
        
        url = f"/api/service-types/{service.id}"
        response = api_client.delete(url)
        
        assert response.status_code == 204
        assert ServiceType.objects.count() == 0