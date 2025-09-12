from django.contrib import admin
from .models import User
# from .models import UserProfile  # Comentar se não existir ainda

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active', 'is_cliente_externo', 'department')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dados Específicos', {'fields': ('role', 'department', 'is_cliente_externo')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    readonly_fields = ('last_login', 'date_joined')

# Comentar temporariamente o UserProfileAdmin até criarmos o modelo UserProfile
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'cargo', 'data_admissao')
#     search_fields = ('user__username', 'user__email', 'cargo')
#     list_filter = ('data_admissao', 'estado_civil')