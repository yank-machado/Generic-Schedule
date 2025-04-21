from ninja_extra import api_controller, route
from django.shortcuts import get_object_or_404
from ninja_extra.pagination import PaginatedResponseSchema, PageNumberPaginationExtra, paginate
from django.contrib.auth.models import User
from user.controllers import UserController
from user.schema import UserCreateIn
from django.db import IntegrityError
from ninja import NinjaAPI

from company.models import Company
from company.schema import (
    CompanyIn, CompanyOut,
)

@api_controller('/companies', tags=['Companies'])
class CompanyController:
    
    @route.get('/', response=PaginatedResponseSchema[CompanyOut])
    @paginate(PageNumberPaginationExtra)
    def list_companies(self):
        companies = Company.objects.all()
        return companies
    
    @route.post('/', response={201: CompanyOut, 400: dict})
    def create_company(self, payload: CompanyIn, user_id: int = None):
        # Verificar se já existe empresa com esse nome
        if Company.objects.filter(name__iexact=payload.name).exists():
            return 400, {"error": "Já existe uma empresa com este nome"}
        
        if user_id:
            user = get_object_or_404(User, id=user_id)
            
            # Verificar se o usuário já tem uma empresa
            if Company.objects.filter(user=user).exists():
                return 400, {"error": "Este usuário já possui uma empresa associada"}
        else:                
            user_payload = UserCreateIn(
                username=f"company_{payload.name.lower().replace(' ', '_')}",
                email=f"{payload.name.lower().replace(' ', '_')}@example.com",
                password="temporary_password",  # Deve ser seguro em produção
                is_company=True,
                company_name=payload.name
            )
            
            # Chamar o controlador de usuário para criar um usuário com perfil de empresa
            user_controller = UserController()
            status, user = user_controller.create_user(user_payload)
            
            if status != 201:
                return status, user  # Retornar erro se a criação do usuário falhar
                
        try:
            company = Company.objects.create(
                user=user,
                name=payload.name,
                description=payload.description
            )
            return 201, company
            
        except IntegrityError as e:
            # Captura qualquer outro erro de integridade não previsto
            return 400, {"error": str(e)}
    
    @route.get('/{company_id}', response=CompanyOut)
    def get_company(self, company_id: int):
        company = get_object_or_404(Company, id=company_id)
        return company
    
    @route.put('/{company_id}', response={200: CompanyOut, 400: dict})
    def update_company(self, company_id: int, payload: CompanyIn):
        company = get_object_or_404(Company, id=company_id)
        
        # Verificar se o novo nome já existe em outra empresa
        if Company.objects.exclude(id=company_id).filter(name__iexact=payload.name).exists():
            return 400, {"error": "Já existe outra empresa com este nome"}
            
        company.name = payload.name
        company.description = payload.description
        company.save()
        return 200, company
    
    @route.delete('/{company_id}', response={204: None, 404: dict})
    def delete_company(self, company_id: int):
        company = get_object_or_404(Company, id=company_id)
        user = company.user
        company.delete()
        user.delete()
        return 204, None