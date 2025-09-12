import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.utils import timezone
import threading

logger = logging.getLogger('apps')
User = get_user_model()

# Thread-local storage para o usuário atual
_user = threading.local()


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para auditoria de requisições.
    Implementa padrão Observer para logging de ações.
    """
    
    def process_request(self, request):
        """Processar requisição de entrada"""
        # Armazenar usuário no thread-local
        if hasattr(request, 'user') and request.user.is_authenticated:
            _user.value = request.user
        else:
            _user.value = None
        
        # Marcar tempo de início
        request._start_time = time.time()
        
        # Log da requisição
        logger.info(f'REQUEST {request.method} {request.path} - User: {getattr(request, "user", "Anonymous")}')
    
    def process_response(self, request, response):
        """Processar resposta"""
        # Calcular tempo de resposta
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log da resposta
            logger.info(f'RESPONSE {response.status_code} {request.path} - Duration: {duration:.3f}s')
        
        # Limpar thread-local
        _user.value = None
        
        return response
    
    def process_exception(self, request, exception):
        """Processar exceções"""
        logger.error(f'EXCEPTION {request.path} - {type(exception).__name__}: {str(exception)}')
        return None


def get_current_user():
    """
    Função utilitária para obter o usuário atual.
    Implementa padrão Singleton para acesso global.
    """
    return getattr(_user, 'value', None)


class BaseService:
    """
    Classe base para services.
    Implementa padrões Template Method e Strategy.
    """
    
    def __init__(self, user=None):
        self.user = user or get_current_user()
    
    def _log_action(self, action, model_name, instance_id=None, extra_data=None):
        """Template Method para logging de ações"""
        log_data = {
            'action': action,
            'model': model_name,
            'instance_id': instance_id,
            'user': self.user.email if self.user else 'system',
            'timestamp': timezone.now().isoformat()
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        logger.info(f'SERVICE_ACTION {log_data}')
    
    def _validate_permissions(self, action, model_class=None):
        """Template Method para validação de permissões"""
        if not self.user:
            raise PermissionError("Usuário não autenticado")
        
        # Implementar validações específicas nas classes filhas
        return True
    
    def _audit_save(self, instance, action='UPDATE'):
        """Template Method para auditoria de salvamento"""
        if hasattr(instance, 'save'):
            instance.save(user=self.user)
        else:
            instance.save()
        
        self._log_action(
            action=action,
            model_name=instance.__class__.__name__,
            instance_id=getattr(instance, 'pk', None)
        )


class DatabaseRouter:
    """
    Router de banco de dados para diferentes ambientes.
    Implementa padrão Strategy para roteamento.
    """
    
    def db_for_read(self, model, **hints):
        """Escolher banco para leitura"""
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Escolher banco para escrita"""
        return 'default'
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Permitir migrações"""
        return True


class CacheMiddleware(MiddlewareMixin):
    """
    Middleware para cache de requisições.
    Implementa padrão Decorator para otimização.
    """
    
    CACHEABLE_PATHS = [
        '/dashboard/',
        '/api/',
    ]
    
    CACHE_DURATION = 300  # 5 minutos
    
    def process_request(self, request):
        """Verificar cache antes de processar requisição"""
        from django.core.cache import cache
        
        # Só cachear GETs
        if request.method != 'GET':
            return None
        
        # Verificar se path é cacheável
        if not any(request.path.startswith(path) for path in self.CACHEABLE_PATHS):
            return None
        
        # Gerar chave do cache
        cache_key = self._generate_cache_key(request)
        
        # Tentar obter do cache
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f'CACHE_HIT {request.path}')
            return cached_response
        
        return None
    
    def process_response(self, request, response):
        """Armazenar resposta no cache"""
        from django.core.cache import cache
        
        # Só cachear responses 200
        if response.status_code != 200:
            return response
        
        # Só cachear GETs
        if request.method != 'GET':
            return response
        
        # Verificar se path é cacheável
        if not any(request.path.startswith(path) for path in self.CACHEABLE_PATHS):
            return response
        
        # Gerar chave do cache e armazenar
        cache_key = self._generate_cache_key(request)
        cache.set(cache_key, response, self.CACHE_DURATION)
        
        logger.info(f'CACHE_SET {request.path}')
        
        return response
    
    def _generate_cache_key(self, request):
        """Gerar chave única para o cache"""
        import hashlib
        
        # Incluir path, query params e usuário
        key_parts = [
            request.path,
            request.GET.urlencode(),
            str(request.user.id) if request.user.is_authenticated else 'anonymous'
        ]
        
        key_string = '|'.join(key_parts)
        return f"page_cache_{hashlib.md5(key_string.encode()).hexdigest()}"


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware de segurança.
    Implementa padrão Chain of Responsibility para validações.
    """
    
    SUSPICIOUS_PATTERNS = [
        'script',
        'javascript:',
        'vbscript:',
        'onload=',
        'onerror=',
        '<iframe',
        'eval(',
    ]
    
    def process_request(self, request):
        """Validar segurança da requisição"""
        # Verificar rate limiting
        if not self._check_rate_limit(request):
            from django.http import HttpResponseTooManyRequests
            return HttpResponseTooManyRequests("Taxa de requisições excedida")
        
        # Verificar padrões suspeitos
        if self._has_suspicious_content(request):
            logger.warning(f'SUSPICIOUS_REQUEST {request.path} - IP: {self._get_client_ip(request)}')
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("Requisição suspeita detectada")
        
        return None
    
    def _check_rate_limit(self, request):
        """Verificar rate limiting por IP"""
        from django.core.cache import cache
        
        client_ip = self._get_client_ip(request)
        cache_key = f"rate_limit_{client_ip}"
        
        # Obter contador atual
        requests_count = cache.get(cache_key, 0)
        
        # Limite: 100 requests por minuto
        if requests_count >= 100:
            return False
        
        # Incrementar contador
        cache.set(cache_key, requests_count + 1, 60)
        return True
    
    def _has_suspicious_content(self, request):
        """Verificar conteúdo suspeito"""
        # Verificar GET params
        for value in request.GET.values():
            if any(pattern.lower() in value.lower() for pattern in self.SUSPICIOUS_PATTERNS):
                return True
        
        # Verificar POST data
        if hasattr(request, 'POST'):
            for value in request.POST.values():
                if any(pattern.lower() in str(value).lower() for pattern in self.SUSPICIOUS_PATTERNS):
                    return True
        
        return False
    
    def _get_client_ip(self, request):
        """Obter IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')