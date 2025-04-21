from ninja_extra import api_controller, route
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja_extra.pagination import PaginatedResponseSchema, PageNumberPaginationExtra, paginate
from django.db import transaction
from user.schema import UserCreateIn, UserOut
from ninja import Schema

class ErrorResponseSchema(Schema):
    detail: str

@api_controller('/users', tags=['Users'])
class UserController:
    
    @route.get('/', response=PaginatedResponseSchema[UserOut])
    @paginate(PageNumberPaginationExtra)
    def list_users(self):
        return User.objects.all()
    
    @route.post('/', response={201: UserOut})
    @transaction.atomic
    def create_user(self, payload: UserCreateIn):
        """
        Create a new user with optional company or client profile
        """
        # Create the user
        user = User.objects.create_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name or '',
            last_name=payload.last_name or ''
        )
        
        # Create company profile if requested
        if payload.is_company:
            if not payload.company_name:
                return 400, {"detail": "Company name is required when is_company=True"}
            
            from company.models import Company
            Company.objects.create(
                user=user,
                name=payload.company_name,
                description=""
            )
        
        # Create client profile if requested
        if payload.is_client:
            if not payload.client_name:
                return 400, {"detail": "Client name is required when is_client=True"}
            
            from client.models import Client
            Client.objects.create(
                user=user,
                name=payload.client_name,
                phone=payload.phone
            )
        
        return 201, user
    
    @route.get('/{user_id}', response=UserOut)
    def get_user(self, user_id: int):
        return get_object_or_404(User, id=user_id)
    
    @route.put('/{user_id}', response=UserOut)
    def update_user(self, user_id: int, payload: UserCreateIn):
        user = get_object_or_404(User, id=user_id)
        
        # Update user fields
        user.username = payload.username
        user.email = payload.email
        
        if payload.password:
            user.set_password(payload.password)
        
        if payload.first_name:
            user.first_name = payload.first_name
        
        if payload.last_name:
            user.last_name = payload.last_name
        
        user.save()
        
        return user
    
    @route.delete('/{user_id}', response={204: None})
    def delete_user(self, user_id: int):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return 204, None

    @route.get('/{user_id}/profile', response={200: dict, 400: ErrorResponseSchema, 500: ErrorResponseSchema})
    def get_user_profile(self, user_id: int):
        """Get the user's profile information (company or client)"""
        user = get_object_or_404(User, id=user_id)
        result = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_company": False,
            "is_client": False,
            "profile_data": None
        }
        
        # Verificar se o usuário tem perfil de empresa
        if hasattr(user, 'company'):
            result["is_company"] = True
            company = user.company
            result["profile_data"] = {
                "company_id": str(company.id),
                "name": company.name,
                "description": company.description
            }
            return 200, result
        
        # Verificar se o usuário tem perfil de cliente
        if hasattr(user, 'client'):
            result["is_client"] = True
            client = user.client
            result["profile_data"] = {
                "client_id": client.id,
                "name": client.name,
                "phone": client.phone
            }
            return 200, result
        
        # Se não tem nenhum perfil
        return 200, result