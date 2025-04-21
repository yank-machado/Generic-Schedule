from ninja_extra import NinjaExtraAPI
from ninja.openapi.docs import Swagger

from company.controllers import CompanyController
from client.controllers import ClientController
from servicetype.controllers import ServiceTypeController
from slot.controllers import SlotController
from booking.controllers import BookingController
from user.controllers import UserController

docs = Swagger(settings={'docExpansion': 'none'})
api = NinjaExtraAPI(title="API de Agendamento", version="1.0.0", docs=docs, urls_namespace="api-1.0.0")

# Registrando os controllers
api.register_controllers(
    CompanyController,
    ClientController,
    ServiceTypeController,
    SlotController,
    BookingController,
    UserController
)