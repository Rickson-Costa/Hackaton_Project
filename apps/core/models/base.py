from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .mixins import TimestampMixin, AuditMixin


class BaseModel(TimestampMixin):
    """
    Modelo base abstrato com campos comuns.
    Implementa o padrão Template Method.
    """
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    
    class Meta:
        abstract = True


class AuditableModel(BaseModel, AuditMixin):
    """
    Modelo base com auditoria.
    Implementa padrões Observer e Strategy para logging.
    """
    
    class Meta:
        abstract = True


class SituacaoMixin(models.Model):
    """
    Mixin para campos de situação.
    Implementa padrão Strategy para diferentes tipos de situação.
    """
    SITUACAO_CHOICES = []  # Sobrescrito nas classes filhas
    
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        verbose_name='Situação'
    )
    
    class Meta:
        abstract = True
    
    def get_situacao_display_formatted(self):
        """Template Method para formatação customizada da situação"""
        return self.get_situacao_display()


class EnderecoMixin(models.Model):
    """
    Mixin para campos de endereço.
    Implementa padrão Composite para dados de endereço.
    """
    cep = models.CharField(max_length=9, blank=True, verbose_name='CEP')
    logradouro = models.CharField(max_length=200, blank=True, verbose_name='Logradouro')
    numero = models.CharField(max_length=10, blank=True, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, blank=True, verbose_name='Cidade')
    uf = models.CharField(max_length=2, blank=True, verbose_name='UF')
    
    class Meta:
        abstract = True
    
    def get_endereco_completo(self):
        """Template Method para formar endereço completo"""
        partes = [
            f"{self.logradouro}, {self.numero}" if self.logradouro else "",
            self.complemento,
            self.bairro,
            f"{self.cidade}/{self.uf}" if self.cidade and self.uf else ""
        ]
        return " - ".join([parte for parte in partes if parte])


class PessoaMixin(models.Model):
    """
    Mixin para dados de pessoa.
    Implementa padrão Strategy para PF/PJ.
    """
    TIPO_PESSOA_CHOICES = [
        (1, 'Pessoa Física'),
        (2, 'Pessoa Jurídica'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name='Nome/Razão Social')
    cpf_cnpj = models.CharField(max_length=18, verbose_name='CPF/CNPJ')
    tipo_pessoa = models.IntegerField(
        choices=TIPO_PESSOA_CHOICES,
        verbose_name='Tipo de Pessoa'
    )
    email = models.EmailField(blank=True, verbose_name='Email')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    
    class Meta:
        abstract = True
    
    def is_pessoa_fisica(self):
        """Strategy Method para identificar PF"""
        return self.tipo_pessoa == 1
    
    def is_pessoa_juridica(self):
        """Strategy Method para identificar PJ"""
        return self.tipo_pessoa == 2
    
    def get_documento_formatado(self):
        """Template Method para formatação do documento"""
        if self.is_pessoa_fisica():
            return self._format_cpf()
        return self._format_cnpj()
    
    def _format_cpf(self):
        """Formatar CPF"""
        cpf = ''.join(filter(str.isdigit, self.cpf_cnpj))
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return self.cpf_cnpj
    
    def _format_cnpj(self):
        """Formatar CNPJ"""
        cnpj = ''.join(filter(str.isdigit, self.cpf_cnpj))
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return self.cpf_cnpj