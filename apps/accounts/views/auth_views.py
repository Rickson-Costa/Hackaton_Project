from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, ListView, DetailView, UpdateView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from apps.accounts.forms.auth_forms import (
    CustomLoginForm, 
    CustomUserCreationForm, 
    UserEditForm
)
from apps.accounts.models import User
from apps.core.middleware import BaseService


class CustomLoginView(LoginView):
    """
    View customizada para login.
    Implementa padrão Template Method para autenticação.
    """
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Strategy Pattern para redirecionamento baseado no tipo de usuário"""
        user = self.request.user
        
        if user.is_cliente():
            return reverse_lazy('projetos:projeto_list')
        elif user.is_ti():
            return reverse_lazy('dashboard:analytics_financeiro')
        else:
            return reverse_lazy('dashboard:index')
    
    def form_valid(self, form):
        """Override para logging de login"""
        response = super().form_valid(form)
        
        # Log do login
        user = form.get_user()
        messages.success(
            self.request, 
            f'Bem-vindo, {user.get_full_name()}!'
        )
        
        # Atualizar último login
        user.save(update_fields=['last_login'])
        
        return response
    
    def form_invalid(self, form):
        """Override para melhor tratamento de erros"""
        messages.error(
            self.request, 
            'Email/usuário ou senha incorretos. Tente novamente.'
        )
        return super().form_invalid(form)


class RegisterView(CreateView):
    """
    View para registro de novos usuários.
    Implementa padrão Factory Method para criação de usuários.
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se registro está habilitado"""
        # Por enquanto, permitir apenas para usuários admin
        if request.user.is_authenticated and not request.user.is_admin():
            messages.warning(request, 'Você não tem permissão para criar novos usuários.')
            return redirect('dashboard:index')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Override para processamento após criação"""
        response = super().form_valid(form)
        
        user = form.instance
        messages.success(
            self.request,
            f'Usuário {user.get_full_name()} criado com sucesso!'
        )
        
        # Log da criação
        service = UserManagementService(user=self.request.user)
        service._log_action(
            action='USER_CREATED',
            model_name='User',
            instance_id=user.id,
            extra_data={'created_user': user.email}
        )
        
        return response


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Lista de usuários para administradores.
    Implementa padrão Strategy para filtragem e ordenação.
    """
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    permission_required = 'accounts.can_manage_users'
    
    def get_queryset(self):
        """Strategy Pattern para filtragem baseada em parâmetros"""
        queryset = User.objects.select_related('profile').order_by('-date_joined')
        
        # Filtros
        search = self.request.GET.get('search')
        role = self.request.GET.get('role')
        department = self.request.GET.get('department')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(role=role)
        
        if department:
            queryset = queryset.filter(department=department)
        
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Opções para filtros
        context['role_choices'] = User.ROLE_CHOICES
        context['department_choices'] = User.DEPARTMENT_CHOICES
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'role': self.request.GET.get('role', ''),
            'department': self.request.GET.get('department', ''),
            'status': self.request.GET.get('status', ''),
        }
        
        # Estatísticas
        context['stats'] = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'admin_users': User.objects.filter(role='admin').count(),
            'client_users': User.objects.filter(is_cliente_externo=True).count(),
        }
        
        return context


class UserDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Detalhes do usuário.
    Implementa padrão Composite para informações complexas.
    """
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'
    permission_required = 'accounts.can_manage_users'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.object
        service = UserAnalyticsService(user=self.request.user)
        
        context.update({
            'user_stats': service.get_user_statistics(user),
            'recent_activity': service.get_recent_activity(user),
            'permissions': service.get_user_permissions(user),
        })
        
        return context


class UserEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Edição de usuário por administradores.
    Implementa padrão Command para modificações controladas.
    """
    model = User
    form_class = UserEditForm
    template_name = 'accounts/user_edit.html'
    permission_required = 'accounts.can_manage_users'
    
    def get_success_url(self):
        return reverse_lazy('accounts:user_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Override para logging de modificações"""
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f'Usuário {self.object.get_full_name()} atualizado com sucesso!'
        )
        
        # Log da modificação
        service = UserManagementService(user=self.request.user)
        service._log_action(
            action='USER_UPDATED',
            model_name='User',
            instance_id=self.object.id,
            extra_data={'updated_user': self.object.email}
        )
        
        return response


class UserToggleStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    Toggle do status ativo/inativo do usuário.
    Implementa padrão Command para operações reversíveis.
    """
    permission_required = 'accounts.can_manage_users'
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        # Não permitir desativar o próprio usuário
        if user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'Você não pode desativar sua própria conta.'
            }, status=400)
        
        # Não permitir desativar superuser
        if user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'Não é possível desativar um superusuário.'
            }, status=400)
        
        # Toggle do status
        user.is_active = not user.is_active
        user.save(user=request.user)
        
        action = 'ativado' if user.is_active else 'desativado'
        
        # Log da ação
        service = UserManagementService(user=request.user)
        service._log_action(
            action='USER_STATUS_CHANGED',
            model_name='User',
            instance_id=user.id,
            extra_data={
                'target_user': user.email,
                'new_status': user.is_active
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Usuário {action} com sucesso.',
            'new_status': user.is_active
        })


# Services para User Management

class UserManagementService(BaseService):
    """
    Service para gerenciamento de usuários.
    Implementa padrões Strategy e Command.
    """
    
    def create_user(self, user_data, user_type='internal'):
        """
        Factory Method para criação de diferentes tipos de usuário.
        """
        try:
            if user_type == 'client':
                return self._create_client_user(user_data)
            else:
                return self._create_internal_user(user_data)
        except Exception as e:
            self._log_action(
                action='USER_CREATION_FAILED',
                model_name='User',
                extra_data={'error': str(e), 'user_data': user_data}
            )
            raise
    
    def _create_internal_user(self, user_data):
        """Strategy para usuário interno"""
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data.get('role', 'analista'),
            department=user_data['department'],
            is_cliente_externo=False
        )
        
        self._log_action(
            action='INTERNAL_USER_CREATED',
            model_name='User',
            instance_id=user.id
        )
        
        return user
    
    def _create_client_user(self, user_data):
        """Strategy para usuário cliente"""
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role='cliente',
            is_cliente_externo=True
        )
        
        self._log_action(
            action='CLIENT_USER_CREATED',
            model_name='User',
            instance_id=user.id
        )
        
        return user
    
    def bulk_update_permissions(self, user_ids, permissions):
        """Command Pattern para atualização em lote"""
        updated_count = 0
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                
                # Aplicar permissões
                for permission, value in permissions.items():
                    if hasattr(user, permission):
                        setattr(user, permission, value)
                
                user.save(user=self.user)
                updated_count += 1
                
            except User.DoesNotExist:
                continue
        
        self._log_action(
            action='BULK_PERMISSIONS_UPDATE',
            model_name='User',
            extra_data={
                'updated_count': updated_count,
                'permissions': permissions
            }
        )
        
        return updated_count


class UserAnalyticsService(BaseService):
    """
    Service para analytics de usuários.
    Implementa padrão Observer para coleta de métricas.
    """
    
    def get_user_statistics(self, user):
        """Factory Method para estatísticas do usuário"""
        from apps.projetos.models import Projeto
        from apps.contratos.models import Contrato
        
        stats = {
            'projetos_criados': 0,
            'projetos_responsavel': 0,
            'contratos_gerenciados': 0,
            'ultimo_login': user.last_login,
            'data_criacao': user.date_joined,
            'ativo_desde': None
        }
        
        if user.can_manage_projects():
            stats['projetos_criados'] = Projeto.objects.filter(
                created_by=user
            ).count()
            stats['projetos_responsavel'] = Projeto.objects.filter(
                responsavel=user
            ).count()
        
        if user.can_manage_contracts():
            stats['contratos_gerenciados'] = Contrato.objects.filter(
                created_by=user
            ).count()
        
        # Calcular tempo ativo
        if user.last_login and user.date_joined:
            stats['ativo_desde'] = (user.last_login - user.date_joined).days
        
        return stats
    
    def get_recent_activity(self, user, limit=10):
        """Obter atividade recente do usuário"""
        # Implementar com base nos logs de auditoria
        activities = []
        
        # Por enquanto, retornar estrutura básica
        return activities[:limit]
    
    def get_user_permissions(self, user):
        """Obter permissões detalhadas do usuário"""
        permissions = {
            'can_manage_projects': user.can_manage_projects(),
            'can_view_financial_data': user.can_view_financial_data(),
            'can_manage_contracts': user.can_manage_contracts(),
            'can_generate_reports': user.has_perm('accounts.can_generate_reports'),
            'can_manage_users': user.has_perm('accounts.can_manage_users'),
            'is_admin': user.is_admin(),
            'is_ti': user.is_ti(),
        }
        
        return permissions
    
    def get_login_analytics(self, days=30):
        """Analytics de login dos últimos N dias"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Implementar analytics detalhados
        return {
            'total_logins': 0,
            'unique_users': 0,
            'avg_session_time': 0,
            'most_active_users': [],
        }