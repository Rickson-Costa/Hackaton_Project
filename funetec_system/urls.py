# Substitua o conteúdo de funetec_system/urls.py por:

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),  # Remover namespace daqui
    path('projetos/', include('apps.projetos.urls')),
    path('contratos/', include('apps.contratos.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('api/', include('apps.api.urls')),
    path('pagamentos/', include('apps.pagamentos.urls')),
    path('relatorios/', include('apps.relatorios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'FUNETEC - Sistema de Gestão'
admin.site.site_title = 'FUNETEC Admin'
admin.site.index_title = 'Administração do Sistema'