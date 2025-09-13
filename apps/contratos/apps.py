# apps/contratos/apps.py
from django.apps import AppConfig

class ContratosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contratos'
    verbose_name = 'Gestão de Contratos'
    
    def ready(self):
        """Importar signals quando o app estiver pronto"""
        try:
            import apps.contratos.signals
        except ImportError:
            pass