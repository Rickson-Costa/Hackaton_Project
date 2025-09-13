from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from .item_contrato import ItemContrato
from apps.projetos.models.ordem import Ordem
from apps.projetos.models.projeto import Projeto

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
        verbose_name='Número do Contrato'
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
        verbose_name='Descrição'
    )
    cpf_cnpj = models.CharField(
        max_length=14,
        db_column='cpfcnpj',
        verbose_name='CPF/CNPJ'
    )
    contratado = models.CharField(
        max_length=150,
        verbose_name='Contratado'
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
        verbose_name='Valor'
    )
    parcelas = models.IntegerField(
        verbose_name='Parcelas'
    )
    data_parcela_inicial = models.DateField(
        db_column='dataParcelaInicial',
        verbose_name='Data Parcela Inicial'
    )
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        verbose_name='Situação'
    )

    @classmethod
    def gerar_numero_contrato(cls):
        """Gera próximo número de contrato no formato NNNN/AAAA"""
        from django.utils import timezone
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

    def __str__(self):
        return f"{self.num_contrato} - {self.contratado}"
    
    def gerar_parcelas(self):
        """Gera as parcelas automaticamente baseado no número de parcelas"""
        from dateutil.relativedelta import relativedelta
        
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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Gerar parcelas automaticamente para contratos novos
        if is_new and self.parcelas > 0:
            self.gerar_parcelas()

    class Meta:
        db_table = 'contrato'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'