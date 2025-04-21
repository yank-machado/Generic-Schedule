import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from company.models import Company

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testcompany', password='password123')

@pytest.fixture
def company_data():
    return {
        'name': 'Test Company',
        'description': 'A test company for API testing'
    }

@pytest.mark.django_db
class TestCompanyAPI:
    
    def test_create_company(self, api_client, user, company_data):
        url = '/api/companies/'
        
        # Adicionar o user_id aos dados da empresa
        data = company_data.copy()
        data['user_id'] = user.id
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201
        assert Company.objects.count() == 1
        
        company = Company.objects.first()
        assert company.name == company_data['name']
        assert company.description == company_data['description']
        assert company.user == user
    
    def test_get_company_list(self, api_client):
        # Criar algumas empresas para testar
        for i in range(3):
            user = User.objects.create_user(username=f'company{i}', password='password123')
            Company.objects.create(user=user, name=f'Company {i}', description=f'Description {i}')
        
        url = '/api/companies/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 3
    
    def test_get_company_detail(self, api_client, user, company_data):
        # Criar uma empresa para testar
        company = Company.objects.create(user=user, **company_data)
        
        url = f'/api/companies/{company.id}/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.data['name'] == company_data['name']
        assert response.data['description'] == company_data['description']
    
    def test_update_company(self, api_client, user, company_data):
        # Criar uma empresa para testar
        company = Company.objects.create(user=user, **company_data)
        
        # Autenticar o cliente API como o usuário da empresa
        api_client.force_authenticate(user=user)
        
        # Dados para atualização
        update_data = {
            'name': 'Updated Company Name',
            'description': 'Updated company description'
        }
        
        url = f'/api/companies/{company.id}/'
        response = api_client.put(url, update_data, format='json')
        
        assert response.status_code == 200
        
        # Verificar se os dados foram atualizados
        company.refresh_from_db()
        assert company.name == update_data['name']
        assert company.description == update_data['description']
    
    def test_delete_company(self, api_client, user, company_data):
        # Criar uma empresa para testar
        company = Company.objects.create(user=user, **company_data)
        
        # Autenticar o cliente API como um admin
        admin = User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')
        api_client.force_authenticate(user=admin)
        
        url = f'/api/companies/{company.id}/'
        response = api_client.delete(url)
        
        assert response.status_code == 204
        assert Company.objects.count() == 0
    
    def test_company_services(self, api_client, user, company_data):
        # Criar uma empresa para testar
        company = Company.objects.create(user=user, **company_data)
        
        url = f'/api/companies/{company.id}/services/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 0  # Inicialmente não há serviços
    
    def test_company_slots(self, api_client, user, company_data):
        # Criar uma empresa para testar
        company = Company.objects.create(user=user, **company_data)
        
        url = f'/api/companies/{company.id}/slots/'
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 0  # Inicialmente não há slots
