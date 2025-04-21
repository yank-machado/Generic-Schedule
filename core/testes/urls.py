from django.urls import path, include
from core.api import api

# Configuração de URLs para testes
# Não podemos definir namespace diretamente em api.urls pois é uma tupla

urlpatterns = [
    path('api/', api.urls),
]