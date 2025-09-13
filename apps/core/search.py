from django.db.models import Q
from apps.projetos.models import Projeto
from apps.contratos.models import Contrato
from apps.accounts.models import User

class GlobalSearchService:
    @staticmethod
    def search_all(query, user):
        """Busca global no sistema"""
        results = {
            'projetos': [],
            'contratos': [],
            'usuarios': [],
            'total': 0
        }
        
        if len(query) < 3:
            return results
        
        # Buscar projetos
        if user.can_manage_projects() or user.is_cliente():
            projetos = Projeto.objects.filter(
                Q(nome__icontains=query) |
                Q(cod_projeto__icontains=query) |
                Q(cliente_nome__icontains=query)
            )
            
            if user.is_cliente():
                projetos = projetos.filter(cliente_email=user.email)
            
            results['projetos'] = projetos[:5]
        
        # Buscar contratos
        if user.can_manage_contracts():
            contratos = Contrato.objects.filter(
                Q(num_contrato__icontains=query) |
                Q(contratado__icontains=query) |
                Q(cpf_cnpj__icontains=query)
            )
            results['contratos'] = contratos[:5]
        
        # Buscar usuários
        if user.is_admin():
            usuarios = User.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(username__icontains=query)
            )
            results['usuarios'] = usuarios[:5]
        
        results['total'] = (
            len(results['projetos']) + 
            len(results['contratos']) + 
            len(results['usuarios'])
        )
        
        return results