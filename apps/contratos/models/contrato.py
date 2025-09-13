# apps/contratos/models/contrato.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

class Contrato(models.Model):
    '''
    Modelo alinhado com tabela contrato
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
        db_column='numContrato',
        verbose_name='Número do Contrato',
        help_text='Formato: NNNN/AAAA (ex: 0001/2025)'
    )
    cod_ordem = models.OneToOneField(
        'projetos.Ordem',
        on_delete=models.PROTECT,
        db_column='codOrdem',
        related_name='contrato',
        verbose_name='Ordem de Serviço'
    )
    descricao = models.CharField(
        max_length=500,
        db_column='objeto',
        verbose_name='Objeto do Contrato'
    )
    cpf_cnpj = models.CharField(
        max_length=18,
        db_column='cpfCnpj',
        verbose_name='CPF/CNPJ do Contratado'
    )
    contratado = models.CharField(
        max_length=150,
        db_column='contratado',
        verbose_name='Nome do Contratado'
    )
    tipo_pessoa = models.IntegerField(
        choices=TIPO_PESSOA_CHOICES,
        db_column='tipoPessoa',
        verbose_name='Tipo de Pessoa'
    )
    data_inicio = models.DateField(
        db_column='dataInicio',
        verbose_name='Data de Início'
    )
    data_fim = models.DateField(
        db_column='dataFim',
        verbose_name='Data de Fim'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        db_column='valor',
        verbose_name='Valor do Contrato'
    )
    parcelas = models.IntegerField(
        default=1,
        db_column='parcelas',
        verbose_name='Quantidade de Parcelas'
    )
    data_parcela_inicial = models.DateField(
        db_column='dataParcelaInicial',
        verbose_name='Data de Vencimento da Primeira Parcela'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='1',
        db_column='situacao',
        verbose_name='Situação'
    )
    
    # Campos calculados
    valor_liquido = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name='Valor Líquido'
    )
    valor_pago = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name='Valor Pago'
    )
    valor_pendente = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name='Valor Pendente'
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='contratos_criados',
        null=True,
        blank=True
    )

    @classmethod
    def gerar_numero_contrato(cls):
        """Gera próximo número de contrato no formato NNNN/AAAA"""
        ano_atual = timezone.now().year
        
        # Buscar último contrato do ano
        ultimo_contrato = cls.objects.filter(
            num_contrato__endswith=f'/{ano_atual}'
        ).order_by('-num_contrato').first()
        
        if ultimo_contrato:
            numero = int(ultimo_contrato.num_contrato.split('/')[0]) + 1
        else:
            numero = 1
        
        return f"{numero:04d}/{ano_atual}"

    def gerar_parcelas(self):
        """Gera as parcelas automaticamente baseado no número de parcelas"""
        from dateutil.relativedelta import relativedelta
        from .item_contrato import ItemContrato
        
        # Limpar parcelas existentes
        self.itens.all().delete()
        
        valor_parcela = self.valor / self.parcelas
        data_vencimento = self.data_parcela_inicial
        
        for i in range(1, self.parcelas + 1):
            ItemContrato.objects.create(
                num_contrato=self,
                cod_lancamento=i,
                data_lancamento=self.data_inicio,
                num_parcela=i,
                valor_parcela=valor_parcela,
                data_vencimento=data_vencimento,
                situacao='1'  # Pendente
            )
            # Próxima parcela: adiciona 1 mês
            data_vencimento = data_vencimento + relativedelta(months=1)

    def atualizar_valores(self):
        """Atualiza valores calculados baseado nas parcelas"""
        parcelas = self.itens.all()
        
        self.valor_pago = sum(item.valor_pago for item in parcelas)
        self.valor_pendente = self.valor - self.valor_pago
        self.valor_liquido = self.valor  # Calcular impostos se necessário
        
        # Atualizar situação baseado no pagamento
        if self.valor_pago >= self.valor:
            self.situacao = '4'  # Finalizado
        elif self.valor_pago > 0:
            self.situacao = '2'  # Em andamento
        
        self.save(update_fields=['valor_pago', 'valor_pendente', 'valor_liquido', 'situacao'])

    def get_percentual_pago(self):
        """Retorna percentual pago do contrato"""
        if self.valor > 0:
            return (self.valor_pago / self.valor) * 100
        return 0

    def tem_parcelas_vencidas(self):
        """Verifica se tem parcelas vencidas"""
        hoje = timezone.now().date()
        return self.itens.filter(
            situacao='1',
            data_vencimento__lt=hoje
        ).exists()

    def get_proxima_parcela(self):
        """Retorna a próxima parcela a vencer"""
        hoje = timezone.now().date()
        return self.itens.filter(
            situacao='1',
            data_vencimento__gte=hoje
        ).order_by('data_vencimento').first()

    def clean(self):
        """Validações customizadas"""
        if self.data_fim <= self.data_inicio:
            raise ValidationError('Data fim deve ser maior que data início')
        
        if self.parcelas <= 0:
            raise ValidationError('Número de parcelas deve ser maior que zero')
        
        if self.valor <= 0:
            raise ValidationError('Valor do contrato deve ser maior que zero')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Gerar número do contrato se novo
        if is_new and not self.num_contrato:
            self.num_contrato = self.gerar_numero_contrato()
        
        # Calcular valor líquido se não definido
        if not self.valor_liquido:
            self.valor_liquido = self.valor
        
        # Calcular valor pendente se não definido
        if not self.valor_pendente:
            self.valor_pendente = self.valor - self.valor_pago
        
        super().save(*args, **kwargs)
        
        # Gerar parcelas automaticamente para contratos novos
        if is_new and self.parcelas > 0:
            try:
                self.gerar_parcelas()
            except ImportError:
                # Se dateutil não estiver disponível, não gerar parcelas automaticamente
                pass

    def __str__(self):
        return f"{self.num_contrato} - {self.contratado}"

    class Meta:
        db_table = 'contrato'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-created_at']