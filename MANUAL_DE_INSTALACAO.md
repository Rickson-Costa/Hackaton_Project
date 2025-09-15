# 🛠️ Manual de Instalação - Sistema FUNETEC

## Sumário
1. [Pré-requisitos](#pré-requisitos)
2. [Instalação Local](#instalação-local)
3. [Instalação no Replit](#instalação-no-replit)
4. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
5. [Configuração de Produção](#configuração-de-produção)
6. [Variáveis de Ambiente](#variáveis-de-ambiente)
7. [Deploy e Monitoramento](#deploy-e-monitoramento)
8. [Solução de Problemas](#solução-de-problemas)

---

## ⚡ Pré-requisitos

### Requisitos de Sistema
- **Python**: 3.10 ou superior
- **Django**: 4.2.7
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Memória RAM**: Mínimo 2GB (recomendado 4GB)
- **Espaço em Disco**: Mínimo 1GB livre

### Dependências Principais
```python
Django==4.2.7
django-crispy-forms==2.1
crispy-bootstrap5==0.7
django-environ==0.11.2
python-decouple==3.8
djangorestframework==3.16.1
gunicorn==23.0.0
psycopg2-binary==2.9.10
pillow==10.1.0
reportlab==4.0.7
mercadopago==2.2.1
```

---

## 💻 Instalação Local

### 1. Clonar o Repositório
```bash
git clone <repository-url>
cd funetec-system
```

### 2. Criar Ambiente Virtual
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
MERCADOPAGO_ACCESS_TOKEN=seu-token-mp
MERCADOPAGO_PUBLIC_KEY=sua-chave-publica-mp
```

### 5. Executar Migrações
```bash
python manage.py migrate
```

### 6. Carregar Dados Iniciais
```bash
python manage.py populate_database --file inserts_postgres.sql
```

### 7. Criar Superusuário
```bash
python manage.py createsuperuser
```

### 8. Executar o Servidor
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🌐 Instalação no Replit

### 1. Importar do GitHub
1. Acesse [Replit.com](https://replit.com)
2. Clique em **"Create Repl"**
3. Selecione **"Import from GitHub"**
4. Cole a URL do repositório
5. Aguarde a importação

### 2. Configuração Automática
O Replit detecta automaticamente:
- **Linguagem**: Python
- **Dependências**: requirements.txt
- **Configuração**: Já otimizada para o ambiente

### 3. Executar Setup
```bash
# O sistema automaticamente:
# 1. Instala as dependências
# 2. Executa migrações
# 3. Popula o banco de dados
# 4. Inicia o servidor na porta 5000
```

### 4. Acessar o Sistema
- **URL**: Fornecida automaticamente pelo Replit
- **Porta**: 5000 (configurada automaticamente)
- **HTTPS**: Habilitado por padrão

### 5. Usuário Padrão
```
Usuário: admin
Email: admin@funetec.org.br
Senha: admin123
```

---

## 🗄️ Configuração do Banco de Dados

### SQLite (Desenvolvimento)
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### PostgreSQL (Produção)
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'funetec_db',
        'USER': 'funetec_user',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Usando DATABASE_URL
```env
# .env
DATABASE_URL=postgresql://user:password@host:port/database
```

---

## 🚀 Configuração de Produção

### 1. Configurações de Segurança
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### 2. Arquivos Estáticos
```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### 3. Configurar Gunicorn
```bash
# Comando para produção
gunicorn --bind 0.0.0.0:8000 --workers 3 funetec_system.wsgi:application
```

### 4. Nginx (Opcional)
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Variáveis de Ambiente

### Configurações Obrigatórias
```env
# Segurança
SECRET_KEY=gere-uma-chave-secreta-forte
DEBUG=False

# Hosts permitidos
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Banco de dados
DATABASE_URL=postgresql://user:pass@host:port/db

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### Configurações do MercadoPago
```env
# Produção
MERCADOPAGO_ACCESS_TOKEN=APP_USR-xxxxxxxx-xxxxxxxx
MERCADOPAGO_PUBLIC_KEY=APP_USR-xxxxxxxx-xxxxxxxx

# Sandbox (testes)
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxx-xxxxxxxx
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxx-xxxxxxxx
```

### Configurações Opcionais
```env
# Cache (Redis)
REDIS_URL=redis://localhost:6379/0

# Logs
LOG_LEVEL=INFO
LOG_FILE=/var/log/funetec/app.log

# Backup
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *  # Todo dia às 2h
```

---

## 📦 Deploy e Monitoramento

### Deploy no Replit
1. **Automatic**: O sistema já está configurado para deploy automático
2. **Manual**: Use o botão "Deploy" no painel do Replit
3. **URL**: Acesse através da URL fornecida
4. **Domínio**: Configure domínio customizado se necessário

### Deploy com Docker
```dockerfile
# Dockerfile já incluído no projeto
docker build -t funetec-system .
docker run -p 8000:8000 funetec-system
```

### Deploy com Docker Compose
```bash
# Usar docker-compose.yml incluído
docker-compose up -d
```

### Monitoramento
- **Logs**: Disponíveis em `/logs/`
- **Health Check**: `/admin/` deve responder
- **Métricas**: Dashboard mostra status do sistema

---

## 🔍 Solução de Problemas

### Problemas Comuns

#### 1. "ModuleNotFoundError"
```bash
# Solução
pip install -r requirements.txt
```

#### 2. "Database doesn't exist"
```bash
# Solução
python manage.py migrate
python manage.py populate_database
```

#### 3. "Static files not found"
```bash
# Solução
python manage.py collectstatic --noinput
```

#### 4. "Permission denied"
```bash
# Linux/Mac
chmod +x manage.py
```

#### 5. "Port already in use"
```bash
# Mudar porta
python manage.py runserver 0.0.0.0:8001
```

### Logs do Sistema
```bash
# Ver logs em tempo real
tail -f logs/access.log
tail -f logs/error.log

# Logs do Django
python manage.py shell
import logging
logger = logging.getLogger('django')
```

### Verificações de Saúde
```bash
# Testar conectividade
python manage.py check

# Testar migrações
python manage.py showmigrations

# Testar admin
python manage.py createsuperuser
```

---

## 📊 Comandos de Gerenciamento

### Comandos Customizados
```bash
# Popular banco de dados
python manage.py populate_database --file inserts_postgres.sql --clear

# Limpar dados (cuidado!)
python manage.py populate_database --clear

# Importar dados específicos
python manage.py populate_database --file dados_customizados.sql
```

### Comandos Django Padrão
```bash
# Migrações
python manage.py makemigrations
python manage.py migrate

# Usuários
python manage.py createsuperuser
python manage.py changepassword username

# Arquivos estáticos
python manage.py collectstatic
python manage.py findstatic arquivo.css

# Shell
python manage.py shell
python manage.py shell_plus  # Se django-extensions instalado
```

---

## 🔐 Configuração de Segurança

### 1. HTTPS
```python
# settings.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. Headers de Segurança
```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 3. Backup do Banco
```bash
# Backup SQLite
cp db.sqlite3 backup/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Backup PostgreSQL
pg_dump funetec_db > backup/funetec_$(date +%Y%m%d_%H%M%S).sql
```

---

## 📞 Suporte Técnico

### Informações para Suporte
Ao relatar problemas, inclua:
- **Versão do Python**: `python --version`
- **Versão do Django**: `python manage.py version`
- **Sistema Operacional**
- **Logs de erro** completos
- **Passos para reproduzir** o problema

### Contatos
- **Email**: ti@funetec.org.br
- **Telefone**: (83) 3000-0000
- **GitHub Issues**: Para bugs e sugestões
- **Documentação**: https://docs.funetec.org.br

---

## 📋 Checklist de Instalação

### ✅ Pré-produção
- [ ] Python 3.10+ instalado
- [ ] Dependências instaladas
- [ ] Banco de dados configurado
- [ ] Migrações executadas
- [ ] Dados iniciais carregados
- [ ] Superusuário criado
- [ ] Arquivos estáticos coletados
- [ ] Variáveis de ambiente configuradas
- [ ] Testes básicos executados

### ✅ Produção
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] HTTPS habilitado
- [ ] Banco de dados de produção
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Logs funcionando
- [ ] Performance testada

---

*Documento gerado em: Setembro 2025*  
*Versão do Sistema: 1.0*  
*FUNETEC-PB - Fundação de Educação, Tecnologia e Cultura da Paraíba*