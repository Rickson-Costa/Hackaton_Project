# apps/accounts/models/profile.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class UserProfile(models.Model):
    """
    Perfil estendido do usuário (decorator).
    """

    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Informações pessoais
    bio = models.TextField('Biografia', blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    rg = models.CharField('RG', max_length=20, blank=True)
    estado_civil = models.CharField(
        'Estado Civil',
        max_length=20,
        choices=ESTADO_CIVIL_CHOICES,
        blank=True
    )

    # Informações profissionais
    cargo = models.CharField('Cargo', max_length=100, blank=True)
    data_admissao = models.DateField('Data de Admissão', null=True, blank=True)

    # Endereço
    cep = models.CharField('CEP', max_length=9, blank=True)
    logradouro = models.CharField('Logradouro', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=10, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    uf = models.CharField('UF', max_length=2, blank=True)

    # Configurações
    notificar_email = models.BooleanField('Notificar por Email', default=True)
    notificar_sistema = models.BooleanField('Notificar no Sistema', default=True)

    # Foto
    avatar = models.ImageField('Foto do Perfil', upload_to='avatars/', null=True, blank=True)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        nome = self.user.get_full_name() or self.user.username
        return f"Perfil de {nome}"

    def get_endereco_completo(self):
        partes = []
        if self.logradouro:
            partes.append(f"{self.logradouro}, {self.numero}" if self.numero else self.logradouro)
        if self.complemento:
            partes.append(self.complemento)
        if self.bairro:
            partes.append(self.bairro)
        if self.cidade and self.uf:
            partes.append(f"{self.cidade}/{self.uf}")
        elif self.cidade:
            partes.append(self.cidade)
        if self.cep:
            partes.append(f"CEP: {self.cep}")
        return " - ".join(partes) if partes else "Endereço não informado"

    def get_idade(self):
        if self.data_nascimento:
            hoje = timezone.now().date()
            return hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None

    def get_tempo_empresa(self):
        if self.data_admissao:
            hoje = timezone.now().date()
            delta = hoje - self.data_admissao
            anos = delta.days // 365
            meses = (delta.days % 365) // 30
            return f"{anos} ano(s) e {meses} mes(es)" if anos > 0 else f"{meses} mes(es)"
        return None
