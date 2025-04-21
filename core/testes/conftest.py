import pytest
from django.urls import reverse, include, path
from django.conf import settings
from django.urls import clear_url_caches, set_urlconf

# Esta função registra os URLs da API para que possam ser usados nos testes
@pytest.fixture(scope='session', autouse=True)
def register_api_urls():
    # Configura as URLs para os testes usando o arquivo urls.py específico para testes
    settings.ROOT_URLCONF = 'core.testes.urls'
    clear_url_caches()
    set_urlconf(None)