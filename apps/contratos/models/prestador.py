# apps/contratos/models/prestador.py
from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models.base import BaseModel
from decimal import Decimal

class Prestador(BaseModel):
    """
    Modelo para Prestadores de Serviço (PF/PJ) - RF-02, RF-21
    """
    
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]
    
    # Dados básicos
    tipo_pessoa = models.CharField(
        'Tipo de Pessoa',
        max_length=2,
        choices=TIPO_PESSOA_CHOICES
    )
    nome = models.CharField(
        'Nome/Razão Social',
        max_length=200,
        help_text='Nome completo para PF ou Razão Social para PJ'
    )
    nome_fantasia = models.CharField(
        'Nome Fantasia',
        max_length=200,
        blank=True,
        help_text='Apenas para PJ'
    )
    
    # Documentos
    cpf = models.CharField(
        'CPF',
        max_length=14,
        blank=True,
        null=True,
        help_text='Apenas para PF'
    )
    cnpj = models.CharField(
        'CNPJ',
        max_length=18,
        blank=True,
        null=True,
        help_text='Apenas para PJ'
    )
    rg = models.CharField(
        'RG',
        max_length=20,
        blank=True,
        help_text='Apenas para PF'
    )
    inscricao_estadual = models.CharField(
        'Inscrição Estadual',
        max_length=20,
        blank=True,
        help_text='Apenas para PJ'
    )
    inscricao_municipal = models.CharField(
        'Inscrição Municipal',
        max_length=20,
        blank=True,
        help_text='Para PJ que prestam serviços'
    )
    
    # Contato
    email = models.EmailField('E-mail')
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    
    # Endereço
    cep = models.CharField('CEP', max_length=10, blank=True)
    logradouro = models.CharField('Logradouro', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=10, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    uf = models.CharField('UF', max_length=2, blank=True)
    
    # Dados bancários
    banco = models.CharField('Banco', max_length=100, blank=True)
    agencia = models.CharField('Agência', max_length=20, blank=True)
    conta = models.CharField('Conta', max_length=20, blank=True)
    tipo_conta = models.CharField(
        'Tipo de Conta',
        max_length=20,
        choices=[
            ('corrente', 'Conta Corrente'),
            ('poupanca', 'Poupança'),
        ],
        blank=True
    )
    
    # Configurações fiscais
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)
    
    class Meta:
        db_table = 'prestador'
        verbose_name = 'Prestador'
        verbose_name_plural = 'Prestadores'
        constraints = [
            models.UniqueConstraint(
                fields=['cpf'],
                condition=models.Q(cpf__isnull=False, tipo_pessoa='PF'),
                name='unique_cpf_when_not_null'
            ),
            models.UniqueConstraint(
                fields=['cnpj'],
                condition=models.Q(cnpj__isnull=False, tipo_pessoa='PJ'),
                name='unique_cnpj_when_not_null'
            ),
        ]
        
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_pessoa_display()})"
    
    def clean(self):
        """Validações específicas para PF/PJ"""
        if self.tipo_pessoa == 'PF':
            if not self.cpf:
                raise ValidationError({'cpf': 'CPF é obrigatório para Pessoa Física'})
            if self.cnpj:
                raise ValidationError({'cnpj': 'CNPJ não deve ser preenchido para Pessoa Física'})
        elif self.tipo_pessoa == 'PJ':
            if not self.cnpj:
                raise ValidationError({'cnpj': 'CNPJ é obrigatório para Pessoa Jurídica'})
            if self.cpf:
                raise ValidationError({'cpf': 'CPF não deve ser preenchido para Pessoa Jurídica'})
    
    def get_documento_principal(self):
        """Retorna o documento principal (CPF ou CNPJ)"""
        return self.cpf if self.tipo_pessoa == 'PF' else self.cnpj
    
    def calcular_retencoes(self, valor_bruto):
        """
        Calcula as retenções conforme RF-21
        PF: INSS, IRRF, ISS
        PJ: ISS, IRRF, PIS/COFINS/CSLL
        """
        retencoes = {}
        valor_liquido = valor_bruto
        
        if self.tipo_pessoa == 'PF':
            # INSS (11% sobre valor bruto até teto)
            teto_inss = Decimal('7507.49')  # Teto INSS 2024
            base_inss = min(valor_bruto, teto_inss)
            inss = base_inss * Decimal('0.11')
            retencoes['inss'] = inss
            valor_liquido -= inss
            
            # IRRF (conforme tabela progressiva)
            if valor_bruto > Decimal('1903.98'):
                irrf = self._calcular_irrf_pf(valor_bruto)
                retencoes['irrf'] = irrf
                valor_liquido -= irrf
            
            # ISS (varia por município, exemplo 5%)
            iss = valor_bruto * Decimal('0.05')
            retencoes['iss'] = iss
            valor_liquido -= iss
            
        elif self.tipo_pessoa == 'PJ':
            # ISS (varia por município, exemplo 5%)
            iss = valor_bruto * Decimal('0.05')
            retencoes['iss'] = iss
            valor_liquido -= iss
            
            # IRRF (1.5% sobre valor bruto)
            irrf = valor_bruto * Decimal('0.015')
            retencoes['irrf'] = irrf
            valor_liquido -= irrf
            
            # PIS/COFINS/CSLL (4.65% total)
            pis_cofins_csll = valor_bruto * Decimal('0.0465')
            retencoes['pis_cofins_csll'] = pis_cofins_csll
            valor_liquido -= pis_cofins_csll
        
        return {
            'valor_bruto': valor_bruto,
            'valor_liquido': valor_liquido,
            'retencoes': retencoes,
            'total_retencoes': sum(retencoes.values())
        }
    
    def _calcular_irrf_pf(self, valor):
        """Calcula IRRF para Pessoa Física conforme tabela progressiva"""
        if valor <= Decimal('1903.98'):
            return Decimal('0')
        elif valor <= Decimal('2826.65'):
            return (valor * Decimal('0.075')) - Decimal('142.80')
        elif valor <= Decimal('3751.05'):
            return (valor * Decimal('0.15')) - Decimal('354.80')
        elif valor <= Decimal('4664.68'):
            return (valor * Decimal('0.225')) - Decimal('636.13')
        else:
            return (valor * Decimal('0.275')) - Decimal('869.36')