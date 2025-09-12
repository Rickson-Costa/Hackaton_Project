from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    """
    Manager para objetos ativos.
    Implementa padrão Strategy para filtragem.
    """
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteManager(models.Manager):
    """
    Manager para soft delete.
    Implementa padrão Strategy para exclusão lógica.
    """
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def deleted(self):
        """Retornar apenas objetos excluídos"""
        return super().get_queryset().filter(deleted_at__isnull=False)
    
    def with_deleted(self):
        """Retornar todos os objetos (incluindo excluídos)"""
        return super().get_queryset()


class ProjetoManager(models.Manager):
    """
    Manager customizado para Projetos.
    Implementa padrões Factory Method e Strategy.
    """
    
    def ativos(self):
        """Projetos ativos (não cancelados nem concluídos)"""
        return self.exclude(situacao__in=['5', '6'])
    
    def em_andamento(self):
        """Projetos em andamento"""
        return self.filter(situacao='2')
    
    def concluidos(self):
        """Projetos concluídos"""
        return self.filter(situacao='6')
    
    def cancelados(self):
        """Projetos cancelados"""
        return self.filter(situacao='5')
    
    def atrasados(self):
        """Projetos atrasados"""
        hoje = timezone.now().date()
        return self.ativos().filter(data_encerramento__lt=hoje)
    
    def proximos_vencimento(self, dias=7):
        """Projetos próximos do vencimento"""
        hoje = timezone.now().date()
        data_limite = hoje + timezone.timedelta(days=dias)
        return self.ativos().filter(
            data_encerramento__gte=hoje,
            data_encerramento__lte=data_limite
        )
    
    def por_responsavel(self, user):
        """Projetos por responsável"""
        return self.filter(responsavel=user)
    
    def por_cliente(self, email_cliente):
        """Projetos por cliente"""
        return self.filter(cliente_email=email_cliente)
    
    def com_orcamento_estourado(self):
        """Projetos com orçamento estourado"""
        return self.filter(valor_realizado__gt=models.F('valor'))
    
    def dashboard_metricas(self):
        """
        Factory Method para métricas do dashboard.
        Retorna dados agregados para visualização.
        """
        hoje = timezone.now().date()
        
        return {
            'total': self.count(),
            'ativos': self.ativos().count(),
            'em_andamento': self.em_andamento().count(),
            'concluidos': self.concluidos().count(),
            'cancelados': self.cancelados().count(),
            'atrasados': self.atrasados().count(),
            'proximos_vencimento': self.proximos_vencimento().count(),
            'valor_total': self.aggregate(total=models.Sum('valor'))['total'] or 0,
            'valor_realizado': self.aggregate(total=models.Sum('valor_realizado'))['total'] or 0,
        }


class ContratoManager(models.Manager):
    """
    Manager customizado para Contratos.
    Implementa padrões Strategy e Observer.
    """
    
    def ativos(self):
        """Contratos ativos"""
        return self.filter(situacao__in=['1', '2'])
    
    def em_andamento(self):
        """Contratos em andamento"""
        return self.filter(situacao='2')
    
    def finalizados(self):
        """Contratos finalizados"""
        return self.filter(situacao='4')
    
    def pessoa_fisica(self):
        """Contratos de pessoa física"""
        return self.filter(tipo_pessoa=1)
    
    def pessoa_juridica(self):
        """Contratos de pessoa jurídica"""
        return self.filter(tipo_pessoa=2)
    
    def com_parcelas_vencidas(self):
        """Contratos com parcelas vencidas"""
        hoje = timezone.now().date()
        return self.pessoa_fisica().filter(
            itens__situacao='1',
            itens__data_vencimento__lt=hoje
        ).distinct()
    
    def proximas_parcelas(self, dias=7):
        """Contratos com parcelas próximas do vencimento"""
        hoje = timezone.now().date()
        data_limite = hoje + timezone.timedelta(days=dias)
        return self.pessoa_fisica().filter(
            itens__situacao='1',
            itens__data_vencimento__gte=hoje,
            itens__data_vencimento__lte=data_limite
        ).distinct()
    
    def por_prestador(self, cpf_cnpj):
        """Contratos por prestador"""
        return self.filter(cpf_cnpj=cpf_cnpj)
    
    def dashboard_financeiro(self):
        """
        Factory Method para métricas financeiras.
        Retorna dados financeiros para dashboard.
        """
        return {
            'total_contratos': self.count(),
            'contratos_ativos': self.ativos().count(),
            'contratos_pf': self.pessoa_fisica().count(),
            'contratos_pj': self.pessoa_juridica().count(),
            'valor_total': self.aggregate(total=models.Sum('valor'))['total'] or 0,
            'valor_pago': self.aggregate(total=models.Sum('valor_pago'))['total'] or 0,
            'valor_pendente': self.aggregate(total=models.Sum('valor_pendente'))['total'] or 0,
            'parcelas_vencidas': self.com_parcelas_vencidas().count(),
            'proximas_parcelas': self.proximas_parcelas().count(),
        }


class ItemContratoManager(models.Manager):
    """
    Manager customizado para Itens de Contrato.
    Implementa padrões Strategy e Chain of Responsibility.
    """
    
    def pendentes(self):
        """Parcelas pendentes"""
        return self.filter(situacao='1')
    
    def liquidadas(self):
        """Parcelas liquidadas"""
        return self.filter(situacao='3')
    
    def vencidas(self):
        """Parcelas vencidas"""
        hoje = timezone.now().date()
        return self.pendentes().filter(data_vencimento__lt=hoje)
    
    def proximas_vencimento(self, dias=7):
        """Parcelas próximas do vencimento"""
        hoje = timezone.now().date()
        data_limite = hoje + timezone.timedelta(days=dias)
        return self.pendentes().filter(
            data_vencimento__gte=hoje,
            data_vencimento__lte=data_limite
        )
    
    def por_contrato(self, num_contrato):
        """Parcelas por contrato"""
        return self.filter(num_contrato=num_contrato)
    
    def relatorio_inadimplencia(self):
        """
        Factory Method para relatório de inadimplência.
        Retorna dados de inadimplência estruturados.
        """
        hoje = timezone.now().date()
        
        vencidas = self.vencidas()
        
        inadimplencia_por_periodo = {}
        for parcela in vencidas:
            dias_atraso = (hoje - parcela.data_vencimento).days
            
            if dias_atraso <= 30:
                periodo = '0-30 dias'
            elif dias_atraso <= 60:
                periodo = '31-60 dias'
            elif dias_atraso <= 90:
                periodo = '61-90 dias'
            else:
                periodo = 'Mais de 90 dias'
            
            if periodo not in inadimplencia_por_periodo:
                inadimplencia_por_periodo[periodo] = {
                    'quantidade': 0,
                    'valor': 0
                }
            
            inadimplencia_por_periodo[periodo]['quantidade'] += 1
            inadimplencia_por_periodo[periodo]['valor'] += float(parcela.get_valor_pendente())
        
        return {
            'total_vencidas': vencidas.count(),
            'valor_vencido': sum(float(p.get_valor_pendente()) for p in vencidas),
            'por_periodo': inadimplencia_por_periodo,
            'proximas_vencimento': self.proximas_vencimento().count(),
        }


class OrderingMixin:
    """
    Mixin para ordenação customizada.
    Implementa padrão Template Method.
    """
    
    def por_data_criacao(self, ordem='desc'):
        """Ordenar por data de criação"""
        if ordem == 'desc':
            return self.order_by('-created_at')
        return self.order_by('created_at')
    
    def por_valor(self, ordem='desc'):
        """Ordenar por valor"""
        if ordem == 'desc':
            return self.order_by('-valor')
        return self.order_by('valor')
    
    def por_situacao(self):
        """Ordenar por situação"""
        return self.order_by('situacao')


class FilterMixin:
    """
    Mixin para filtros customizados.
    Implementa padrão Strategy para diferentes filtros.
    """
    
    def por_periodo(self, data_inicio, data_fim, campo='created_at'):
        """Filtrar por período"""
        filtro = {
            f'{campo}__gte': data_inicio,
            f'{campo}__lte': data_fim
        }
        return self.filter(**filtro)
    
    def por_ano(self, ano, campo='created_at'):
        """Filtrar por ano"""
        return self.filter(**{f'{campo}__year': ano})
    
    def por_mes(self, ano, mes, campo='created_at'):
        """Filtrar por mês"""
        return self.filter(**{f'{campo}__year': ano, f'{campo}__month': mes})


class AggregationMixin:
    """
    Mixin para agregações customizadas.
    Implementa padrão Template Method para cálculos.
    """
    
    def valor_total(self, campo='valor'):
        """Calcular valor total"""
        return self.aggregate(total=models.Sum(campo))['total'] or 0
    
    def valor_medio(self, campo='valor'):
        """Calcular valor médio"""
        return self.aggregate(media=models.Avg(campo))['media'] or 0
    
    def contar_por_situacao(self):
        """Contar por situação"""
        return self.values('situacao').annotate(
            count=models.Count('id')
        ).order_by('situacao')
    
    def resumo_financeiro(self):
        """Resumo financeiro completo"""
        return self.aggregate(
            total=models.Sum('valor'),
            media=models.Avg('valor'),
            maximo=models.Max('valor'),
            minimo=models.Min('valor'),
            count=models.Count('id')
        )