from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

class Contrato(models.Model):
    '''
    Modelo simplificado para Contratos.
    '''
    
    SITUACAO_CHOICES = [
        ('1', 'Lançado'),
        ('2', 'Em andamento'),
        ('3', 'Cancelado'),
        ('4', 'Finalizado'),
    ]
    
    TIPO_PESSOA_CHOICES = [
        (1, 'Pessoa Física'),
        (2, 'Pessoa Jurídica'),
    ]
    
    num_contrato = models.CharField(
        max_length=10,
        primary_key=True,
        verbose_name='Número do Contrato',
        help_text='Formato: NNNN/AAAA (ex: 0001/2025)',
        db_column='numContrato'
    )
    cod_ordem = models.OneToOneField(
        'projetos.Ordem',
        on_delete=models.PROTECT,
        related_name='contrato',
        verbose_name='Ordem de Serviço',
        db_column='codOrdem'
    )
    descricao = models.CharField(
        max_length=500,
        verbose_name='Descrição do Contrato',
        db_column='objeto'
    )
    cpf_cnpj = models.CharField(
        max_length=18,
        verbose_name='CPF/CNPJ do Contratado',
        db_column='cpfCnpj'
    )
    contratado = models.CharField(
        max_length=150,
        verbose_name='Nome do Contratado',
        db_column='contratado'
    )
    tipo_pessoa = models.IntegerField(
        choices=TIPO_PESSOA_CHOICES,
        verbose_name='Tipo de Pessoa',
        db_column='tipoPessoa'
    )
    data_inicio = models.DateField(
        verbose_name='Data de Início',
        db_column='dataInicio'
    )
    data_fim = models.DateField(
        verbose_name='Data de Fim',
        db_column='dataFim'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor do Contrato',
        db_column='valor'
    )
    parcelas = models.IntegerField(
        verbose_name='Quantidade de Parcelas',
        default=1,
        db_column='parcelas'
    )
    data_parcela_inicial = models.DateField(
        verbose_name='Data de Vencimento da Primeira Parcela',
        db_column='dataParcelaInicial'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',
        verbose_name='Situação',
        db_column='situacao'
    )
    
    # Campos de controle simplificados
    valor_liquido = models.DecimalField(
        'Valor Líquido',
        max_digits=14,
        decimal_places=2,
        default=0
    )
    valor_pago = models.DecimalField(
        'Valor Pago',
        max_digits=14,
        decimal_places=2,
        default=0
    )
    valor_pendente = models.DecimalField(
        'Valor Pendente',
        max_digits=14,
        decimal_places=2,
        default=0
    )
    
    # Campos de auditoria básicos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='contratos_criados',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'contrato'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Contrato {self.num_contrato} - {self.contratado}"
    
    def clean(self):
        '''Validação básica'''
        super().clean()
        
        if self.data_fim and self.data_inicio:
            if self.data_fim < self.data_inicio:
                raise ValidationError('Data de fim deve ser maior que data de início.')
    
    def save(self, *args, **kwargs):
        '''Override básico do save'''
        # Cálculos básicos
        if not self.valor_liquido:
            self.valor_liquido = self.valor
        
        if not self.valor_pendente:
            self.valor_pendente = self.valor_liquido - self.valor_pago
        
        super().save(*args, **kwargs)
    
    @classmethod
    def gerar_numero_contrato(cls, ano=None):
        '''Gerar número do contrato'''
        if ano is None:
            ano = timezone.now().year
        
        try:
            ultimo_contrato = cls.objects.filter(
                num_contrato__endswith=f'/{ano}'
            ).order_by('-num_contrato').first()
            
            if ultimo_contrato:
                numero = int(ultimo_contrato.num_contrato.split('/')[0]) + 1
            else:
                numero = 1
        except:
            numero = 1
        
        return f"{numero:04d}/{ano}"


class Prestador(models.Model):
    '''
    Modelo simplificado para Prestadores de Serviço.
    '''
    
    TIPO_PESSOA_CHOICES = [
        (1, 'Pessoa Física'),
        (2, 'Pessoa Jurídica'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name='Nome/Razão Social')
    cpf_cnpj = models.CharField(max_length=18, verbose_name='CPF/CNPJ', unique=True)
    tipo_pessoa = models.IntegerField(
        choices=TIPO_PESSOA_CHOICES,
        verbose_name='Tipo de Pessoa'
    )
    email = models.EmailField(blank=True, verbose_name='Email')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    
    # Campos de auditoria básicos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Prestador'
        verbose_name_plural = 'Prestadores'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.cpf_cnpj})"