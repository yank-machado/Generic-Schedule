from ninja_extra import api_controller, route
from django.shortcuts import get_object_or_404
from ninja_extra.pagination import PaginatedResponseSchema, PageNumberPaginationExtra, paginate
from client.models import Client, User
from client.schema import ClientIn, ClientOut


@api_controller('/clients', tags=['Clients'])
class ClientController:
    
    @route.get('/', response=PaginatedResponseSchema[ClientOut])
    @paginate(PageNumberPaginationExtra)
    def list_clients(self):
        return Client.objects.all()
    
    @route.post('/', response={201: ClientOut})
    def create_client(self, payload: ClientIn, user_id: int = None):
        """Create a client profile for a user"""
        if user_id:

            user = get_object_or_404(User, id=user_id)
        else:
            from user.controllers import UserController
            from user.schema import UserCreateIn
            
            user_payload = UserCreateIn(
                username=f"client_{payload.name.lower().replace(' ', '_')}",
                email=f"{payload.name.lower().replace(' ', '_')}@example.com",
                password="temporary_password",  
                is_client=True,
                client_name=payload.name,
                phone=payload.phone
            )
            
            user_controller = UserController()
            status, user = user_controller.create_user(user_payload)
            
            if status != 201:
                return status, user  
        client = Client.objects.create(
            user=user,
            name=payload.name,
            phone=payload.phone
        )
        return 201, client
    
    @route.get('/{client_id}', response=ClientOut)
    def get_client(self, client_id: int):
        return get_object_or_404(Client, id=client_id)
    
    @route.put('/{client_id}', response=ClientOut)
    def update_client(self, client_id: int, payload: ClientIn):
        client = get_object_or_404(Client, id=client_id)
        client.name = payload.name
        client.phone = payload.phone
        client.save()
        return client
    
    @route.delete('/{client_id}', response={204: None})
    def delete_client(self, client_id: int):
        client = get_object_or_404(Client, id=client_id)
        user = client.user
        client.delete()
        user.delete()
        return 204, None