# apps/contratos/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Contrato, ItemContrato

class ItemContratoInline(admin.TabularInline):
    model = ItemContrato
    extra = 0
    readonly_fields = ('cod_lancamento', 'data_lancamento', 'valor_pago', 'data_pagamento')
    fields = (
        'num_parcela', 'valor_parcela', 'data_vencimento', 
        'valor_pago', 'data_pagamento', 'situacao', 'observacoes'
    )
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        'num_contrato', 'contratado', 'get_tipo_pessoa_display', 
        'valor_display', 'get_progresso', 'situacao_display', 
        'data_inicio', 'parcelas', 'get_actions'
    )
    list_filter = ('situacao', 'tipo_pessoa', 'data_inicio', 'created_at')
    search_fields = ('num_contrato', 'contratado', 'cpf_cnpj', 'descricao')
    readonly_fields = (
        'num_contrato', 'valor_liquido', 'valor_pago', 'valor_pendente',
        'created_at', 'updated_at', 'created_by'
    )
    inlines = [ItemContratoInline]
    
    fieldsets = (
        ('Identificação', {
            'fields': ('num_contrato', 'cod_ordem', 'descricao', 'situacao')
        }),
        ('Dados do Contratado', {
            'fields': ('contratado', 'tipo_pessoa', 'cpf_cnpj')
        }),
        ('Vigência e Valores', {
            'fields': (
                ('data_inicio', 'data_fim'),
                ('valor', 'valor_liquido'),
                ('valor_pago', 'valor_pendente'),
                ('parcelas', 'data_parcela_inicial')
            )
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def valor_display(self, obj):
        return format_html(
            '<strong>R$ {:,.2f}</strong>',
            obj.valor
        )
    valor_display.short_description = 'Valor'
    valor_display.admin_order_field = 'valor'
    
    def get_progresso(self, obj):
        percentual = obj.get_percentual_pago()
        cor = 'success' if percentual >= 100 else 'warning' if percentual >= 50 else 'danger'
        
        return format_html(
            '<div class="progress" style="width: 100px; height: 20px;">'
            '<div class="progress-bar bg-{}" style="width: {}%">{:.1f}%</div>'
            '</div>',
            cor, percentual, percentual
        )
    get_progresso.short_description = 'Progresso'
    
    def situacao_display(self, obj):
        cores = {
            '1': 'secondary',
            '2': 'primary', 
            '3': 'danger',
            '4': 'success'
        }
        cor = cores.get(obj.situacao, 'secondary')
        
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            cor, obj.get_situacao_display()
        )
    situacao_display.short_description = 'Situação'
    
    def get_actions(self, obj):
        """Ações rápidas no admin"""
        actions = []
        
        if obj.situacao in ['1', '2']:
            actions.append(
                format_html(
                    '<a class="btn btn-sm btn-outline-success" href="{}">Pagamentos</a>',
                    reverse('admin:contratos_itemcontrato_changelist') + f'?num_contrato__exact={obj.pk}'
                )
            )
        
        actions.append(
            format_html(
                '<a class="btn btn-sm btn-outline-primary" href="{}">Ver</a>',
                reverse('contratos:contrato_detail', args=[obj.pk])
            )
        )
        
        return mark_safe(' '.join(actions))
    get_actions.short_description = 'Ações'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ItemContrato)
class ItemContratoAdmin(admin.ModelAdmin):
    list_display = (
        'get_contrato_link', 'num_parcela', 'valor_parcela_display',
        'data_vencimento', 'get_status', 'get_atraso', 'get_actions'
    )
    list_filter = ('situacao', 'data_vencimento', 'num_contrato__tipo_pessoa')
    search_fields = (
        'num_contrato__num_contrato', 'num_contrato__contratado', 
        'num_contrato__cpf_cnpj'
    )
    readonly_fields = ('cod_lancamento', 'data_lancamento', 'get_valor_pendente')
    date_hierarchy = 'data_vencimento'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('num_contrato', 'num_parcela', 'cod_lancamento', 'data_lancamento')
        }),
        ('Valores', {
            'fields': (
                ('valor_parcela', 'valor_pago'),
                'get_valor_pendente'
            )
        }),
        ('Datas', {
            'fields': ('data_vencimento', 'data_pagamento')
        }),
        ('Status', {
            'fields': ('situacao', 'observacoes')
        })
    )
    
    def get_contrato_link(self, obj):
        url = reverse('admin:contratos_contrato_change', args=[obj.num_contrato.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.num_contrato.num_contrato
        )
    get_contrato_link.short_description = 'Contrato'
    get_contrato_link.admin_order_field = 'num_contrato__num_contrato'
    
    def valor_parcela_display(self, obj):
        return format_html(
            'R$ {:,.2f}',
            obj.valor_parcela
        )
    valor_parcela_display.short_description = 'Valor'
    valor_parcela_display.admin_order_field = 'valor_parcela'
    
    def get_status(self, obj):
        cores = {
            '1': 'warning',
            '2': 'secondary',
            '3': 'success', 
            '4': 'info'
        }
        cor = cores.get(obj.situacao, 'secondary')
        
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            cor, obj.get_situacao_display()
        )
    get_status.short_description = 'Status'
    
    def get_atraso(self, obj):
        if obj.is_vencida():
            dias = obj.get_dias_atraso()
            return format_html(
                '<span class="text-danger"><strong>{} dia{} de atraso</strong></span>',
                dias, 's' if dias != 1 else ''
            )
        elif obj.data_vencimento == timezone.now().date():
            return format_html('<span class="text-warning"><strong>Vence hoje!</strong></span>')
        else:
            return 'Em dia'
    get_atraso.short_description = 'Situação'
    
    def get_valor_pendente(self, obj):
        return format_html(
            'R$ {:,.2f}',
            obj.get_valor_pendente()
        )
    get_valor_pendente.short_description = 'Valor Pendente'
    
    def get_actions(self, obj):
        """Ações rápidas no admin"""
        actions = []
        
        if obj.pode_receber_pagamento():
            actions.append(
                format_html(
                    '<a class="btn btn-sm btn-success" href="{}">Pagar</a>',
                    reverse('contratos:registrar-pagamento', args=[obj.pk])
                )
            )
        
        actions.append(
            format_html(
                '<a class="btn btn-sm btn-outline-primary" href="{}">Contrato</a>',
                reverse('contratos:contrato_detail', args=[obj.num_contrato.pk])
            )
        )
        
        return mark_safe(' '.join(actions))
    get_actions.short_description = 'Ações'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('num_contrato')

# Customizar o admin site
admin.site.site_header = "FUNETEC - Administração"
admin.site.site_title = "FUNETEC Admin"
admin.site.index_title = "Gestão de Projetos e Contratos"