from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('ti', 'TI'),
        ('fiscal', 'Fiscal'),
        ('financeiro', 'Financeiro'),
        ('analista', 'Analista'),
        ('cliente', 'Cliente'),
    ]

    DEPARTMENT_CHOICES = [
        ('administrativo', 'Administrativo'),
        ('financeiro', 'Financeiro'),
        ('ti', 'Tecnologia da Informação'),
        ('fiscal', 'Fiscal'),
        ('operacional', 'Operacional'),
        ('diretoria', 'Diretoria'),
    ]

    cpf = models.CharField(
        'CPF', max_length=14, unique=True, null=True, blank=True,
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$',
            message='CPF deve estar no formato XXX.XXX.XXX-XX ou apenas números'
        )]
    )
    telefone = models.CharField('Telefone', max_length=20, blank=True)

    role = models.CharField('Função', max_length=20, choices=ROLE_CHOICES, default='analista')
    department = models.CharField('Departamento', max_length=30, choices=DEPARTMENT_CHOICES, blank=True)
    is_cliente_externo = models.BooleanField('Cliente Externo', default=False, help_text='Indica se é um cliente externo da FUNETEC')

    last_activity = models.DateTimeField('Última Atividade', null=True, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-date_joined']
        permissions = [
            ('can_manage_users', 'Pode gerenciar usuários'),
            ('can_view_financial_data', 'Pode ver dados financeiros'),
            ('can_manage_contracts', 'Pode gerenciar contratos'),
            ('can_manage_projects', 'Pode gerenciar projetos'),
            ('can_generate_reports', 'Pode gerar relatórios'),
        ]

    def __str__(self):
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = ''.join(filter(str.isdigit, self.cpf))
        if self.is_cliente_externo:
            self.role = 'cliente'
            self.department = ''
        super().save(*args, **kwargs)
    
    # Strategy Methods para permissões baseadas em role
    def is_admin(self):
        """Verificar se é administrador"""
        return self.role == 'admin' or self.is_superuser
    
    def is_ti(self):
        """Verificar se é da TI"""
        return self.role == 'ti' or self.is_admin()
    
    def is_fiscal(self):
        """Verificar se é fiscal"""
        return self.role == 'fiscal'
    
    def is_financeiro(self):
        """Verificar se é do financeiro"""
        return self.role == 'financeiro'
    
    def is_cliente(self):
        """Verificar se é cliente"""
        return self.role == 'cliente' or self.is_cliente_externo
    
    def can_manage_projects(self):
        """Verificar se pode gerenciar projetos"""
        return self.is_admin() or self.has_perm('accounts.can_manage_projects')
    
    def can_view_financial_data(self):
        """Verificar se pode ver dados financeiros"""
        return self.role in ['admin', 'financeiro', 'fiscal'] or self.has_perm('accounts.can_view_financial_data')
    
    def can_manage_contracts(self):
        """Verificar se pode gerenciar contratos"""
        return self.role in ['admin', 'financeiro'] or self.has_perm('accounts.can_manage_contracts')
    
    def can_generate_reports(self):
        """Verificar se pode gerar relatórios"""
        return not self.is_cliente() or self.has_perm('accounts.can_generate_reports')
    
    def can_manage_users(self):
        """Verificar se pode gerenciar usuários"""
        return self.is_admin() or self.has_perm('accounts.can_manage_users')
    
    def get_accessible_projects(self):
        """Factory Method para obter projetos acessíveis"""
        from apps.projetos.models import Projeto
        
        if self.can_manage_projects():
            return Projeto.objects.all()
        elif self.is_cliente():
            return Projeto.objects.filter(cliente_email=self.email)
        else:
            return Projeto.objects.filter(responsavel=self)
    
    def get_dashboard_widgets(self):
        """Factory Method para widgets do dashboard baseado no role"""
        widgets = ['projetos_overview', 'alertas']
        
        if self.can_view_financial_data():
            widgets.extend(['financeiro_overview', 'contratos_overview'])
        
        if self.is_admin():
            widgets.extend(['usuarios_overview', 'sistema_status'])
        
        if self.is_cliente():
            widgets = ['meus_projetos', 'proximos_pagamentos']
        
        return widgets
    
    def update_last_activity(self):
        """Atualizar última atividade"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

