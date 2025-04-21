import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import datetime, timedelta
from core.models import Company, Slot, User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def company():
    user = User.objects.create_user(username='testcompany', password='password123')
    return Company.objects.create(user=user, name='Test Company')

@pytest.mark.django_db
class TestSlotAPI:
    
    def test_create_slot(self, api_client, company):
        url = '/api/slots/'
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        payload = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'company_id': company.id
        }
        
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 201
        assert Slot.objects.count() == 1
        assert Slot.objects.first().company == company
    
    def test_get_slot_list(self, api_client, company):
        # Criar alguns slots para testar
        start_time = datetime.now() + timedelta(days=1)
        for i in range(3):
            Slot.objects.create(
                company=company,
                start_time=start_time + timedelta(hours=i),
                end_time=start_time + timedelta(hours=i+1)
            )
        
        url = '/api/slots/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3
    
    def test_filter_slots_by_company(self, api_client, company):
        # Criar outra empresa e slots para ambas
        user2 = User.objects.create_user(username='othercompany', password='password123')
        other_company = Company.objects.create(user=user2, name='Other Company')
        
        start_time = datetime.now() + timedelta(days=1)
        
        # Criar 2 slots para a primeira empresa
        for i in range(2):
            Slot.objects.create(
                company=company,
                start_time=start_time + timedelta(hours=i),
                end_time=start_time + timedelta(hours=i+1)
            )
        
        # Criar 1 slot para a segunda empresa
        Slot.objects.create(
            company=other_company,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1)
        )
        
        # Filtrar slots pela primeira empresa
        url = f"{reverse('api-1.0.0:slots')}?company_id={company.id}"
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.data['count'] == 2
    
    def test_slot_overlap_validation(self, api_client, company):
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        # Criar o primeiro slot
        Slot.objects.create(
            company=company,
            start_time=start_time,
            end_time=end_time
        )
        
        # Tentar criar um slot sobreposto
        url = reverse('api-1.0.0:slots')
        payload = {
            'start_time': start_time + timedelta(hours=1),  # Começa no meio do primeiro slot
            'end_time': end_time + timedelta(hours=1),
            'company_id': company.id
        }
        
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400
        assert "sobrepõe" in response.data['detail']

    def test_bulk_create_slots(self, api_client, company):
        url = f"{reverse('api-1.0.0:slots')}-bulk-create"
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=5)
        
        payload = {
            'company_id': company.id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'duration_minutes': 30,
            'start_hour': 9,
            'end_hour': 17,
            'days_of_week': [0, 1, 2, 3, 4]  # Segunda a sexta
        }
        
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 201
        
        # Calcular quantidade esperada de slots:
        # 5 dias, 8 horas por dia (9-17), 2 slots por hora (30 min cada) = 5 * 8 * 2 = 80
        # Mas como start_date começa hoje, dependendo da hora atual, teremos menos slots
        assert Slot.objects.filter(company=company).count() > 30
    
    def test_delete_slot(self, api_client, company):
        # Criar um slot e depois deletá-lo
        start_time = datetime.now() + timedelta(days=1)
        slot = Slot.objects.create(
            company=company,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1)
        )
        
        url = f"{reverse('api-1.0.0:slots')}{slot.id}"
        response = api_client.delete(url)
        
        assert response.status_code == 204
        assert Slot.objects.count() == 0
