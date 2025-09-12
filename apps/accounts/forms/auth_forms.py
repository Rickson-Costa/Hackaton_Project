from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML, Div, Row, Column
from crispy_forms.bootstrap import InlineRadios
from apps.accounts.models import UserProfile

User = get_user_model()


class CustomLoginForm(AuthenticationForm):
    """
    Formulário de login customizado.
    Implementa padrão Strategy para diferentes tipos de autenticação.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'login-form'
        
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email ou usuário',
            'autofocus': True
        })
        
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })
        
        self.helper.layout = Layout(
            HTML('<div class="text-center mb-4"><h3>Entrar no Sistema</h3></div>'),
            Field('username', css_class='mb-3'),
            Field('password', css_class='mb-3'),
            HTML(
                '<div class="d-flex justify-content-between align-items-center mb-3">'
                '<div class="form-check">'
                '<input type="checkbox" class="form-check-input" id="remember_me" name="remember_me">'
                '<label class="form-check-label" for="remember_me">Lembrar-me</label>'
                '</div>'
                '</div>'
            ),
            Submit(
                'submit', 
                'Entrar', 
                css_class='btn btn-primary w-100 mb-3'
            ),
            HTML(
                '<div class="text-center">'
                '<p class="mb-0">Não tem uma conta? '
                '<a href="{% url \'accounts:register\' %}" class="text-decoration-none">Cadastre-se</a></p>'
                '</div>'
            )
        )


class CustomUserCreationForm(UserCreationForm):
    """
    Formulário de criação de usuário customizado.
    Implementa padrão Builder para construção de usuários.
    """
    
    email = forms.EmailField(
        required=True,
        help_text='Email será usado para login e notificações'
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nome'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Sobrenome'
    )
    cpf = forms.CharField(
        max_length=14,
        required=False,
        label='CPF',
        help_text='Apenas números ou formato XXX.XXX.XXX-XX'
    )
    telefone = forms.CharField(
        max_length=20,
        required=False,
        label='Telefone'
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='analista',
        label='Função',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.ChoiceField(
        choices=[('', '-- Selecione --')] + User.DEPARTMENT_CHOICES,
        required=False,
        label='Departamento',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_cliente_externo = forms.BooleanField(
        required=False,
        label='Cliente Externo',
        help_text='Marque se for cliente externo da FUNETEC'
    )
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 
            'cpf', 'telefone', 'role', 'department', 
            'is_cliente_externo', 'password1', 'password2'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'registration-form'
        
        # Customizar widgets
        self.fields['username'].help_text = 'Nome de usuário único para login'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres'
        
        self.helper.layout = Layout(
            HTML('<div class="text-center mb-4"><h3>Criar Nova Conta</h3></div>'),
            
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('username', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('cpf', css_class='form-group col-md-6'),
                Column('telefone', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Field('is_cliente_externo', css_class='mb-3'),
            
            HTML(
                '<div id="internal-user-fields" style="display: none;">'
            ),
            Row(
                Column('role', css_class='form-group col-md-6'),
                Column('department', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            HTML('</div>'),
            
            Row(
                Column('password1', css_class='form-group col-md-6'),
                Column('password2', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Submit(
                'submit', 
                'Criar Conta', 
                css_class='btn btn-success w-100 mb-3'
            ),
            
            HTML(
                '<div class="text-center">'
                '<p class="mb-0">Já tem uma conta? '
                '<a href="{% url \'accounts:login\' %}" class="text-decoration-none">Fazer login</a></p>'
                '</div>'
            )
        )
    
    def clean_email(self):
        """Validar email único"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está em uso.')
        return email
    
    def clean_cpf(self):
        """Validar e formatar CPF"""
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remover formatação
            cpf = ''.join(filter(str.isdigit, cpf))
            
            # Validar tamanho
            if len(cpf) != 11:
                raise forms.ValidationError('CPF deve ter 11 dígitos.')
            
            # Verificar se já existe
            if User.objects.filter(cpf=cpf).exists():
                raise forms.ValidationError('Este CPF já está cadastrado.')
            
            return cpf
        return cpf
    
    def clean(self):
        """Validação customizada"""
        cleaned_data = super().clean()
        
        is_cliente_externo = cleaned_data.get('is_cliente_externo')
        department = cleaned_data.get('department')
        
        # Departamento obrigatório para funcionários internos
        if not is_cliente_externo and not department:
            raise forms.ValidationError(
                'Departamento é obrigatório para funcionários internos.'
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Override do save para campos customizados"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.cpf = self.cleaned_data.get('cpf')
        user.telefone = self.cleaned_data.get('telefone')
        user.role = self.cleaned_data['role']
        user.department = self.cleaned_data.get('department')
        user.is_cliente_externo = self.cleaned_data.get('is_cliente_externo', False)
        
        if commit:
            user.save()
        
        return user


class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição de perfil.
    Implementa padrão Composite para dados complexos.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'data_nascimento', 'rg', 'estado_civil',
            'cargo', 'data_admissao', 'cep', 'logradouro',
            'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'notificar_email', 'notificar_sistema'
        ]
        
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'estado_civil': forms.Select(),
            'uf': forms.Select(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'profile-form'
        
        # Choices para UF
        UF_CHOICES = [
            ('', '-- Selecione --'),
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
            ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
            ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
            ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
        ]
        
        self.fields['uf'].choices = UF_CHOICES
        
        self.helper.layout = Layout(
            HTML('<h4>Informações Pessoais</h4>'),
            
            'bio',
            
            Row(
                Column('data_nascimento', css_class='form-group col-md-4'),
                Column('rg', css_class='form-group col-md-4'),
                Column('estado_civil', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Informações Profissionais</h4>'),
            
            Row(
                Column('cargo', css_class='form-group col-md-6'),
                Column('data_admissao', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            HTML('<h4 class="mt-4">Endereço</h4>'),
            
            Row(
                Column('cep', css_class='form-group col-md-3'),
                Column('logradouro', css_class='form-group col-md-6'),
                Column('numero', css_class='form-group col-md-3'),
                css_class='form-row'
            ),
            
            Row(
                Column('complemento', css_class='form-group col-md-4'),
                Column('bairro', css_class='form-group col-md-4'),
                Column('cidade', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            
            Field('uf'),
            
            HTML('<h4 class="mt-4">Notificações</h4>'),
            
            Row(
                Column('notificar_email', css_class='form-group col-md-6'),
                Column('notificar_sistema', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Submit(
                'submit', 
                'Salvar Perfil', 
                css_class='btn btn-primary'
            )
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulário customizado para alteração de senha"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            HTML('<h4>Alterar Senha</h4>'),
            
            Field('old_password', css_class='mb-3'),
            Field('new_password1', css_class='mb-3'),
            Field('new_password2', css_class='mb-3'),
            
            Submit(
                'submit', 
                'Alterar Senha', 
                css_class='btn btn-primary'
            )
        )


class UserEditForm(forms.ModelForm):
    """
    Formulário para edição de usuário por administradores.
    Implementa padrão Factory Method para diferentes tipos de usuário.
    """
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'cpf', 'telefone', 'role', 'department',
            'is_active', 'is_cliente_externo'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            HTML('<h4>Editar Usuário</h4>'),
            
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('username', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('cpf', css_class='form-group col-md-6'),
                Column('telefone', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('role', css_class='form-group col-md-6'),
                Column('department', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Row(
                Column('is_active', css_class='form-group col-md-6'),
                Column('is_cliente_externo', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            
            Submit(
                'submit', 
                'Salvar Alterações', 
                css_class='btn btn-primary'
            )
        )