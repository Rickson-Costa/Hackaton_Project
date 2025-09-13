from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.search import GlobalSearchService

class GlobalSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 3:
            return JsonResponse({'results': [], 'message': 'Digite pelo menos 3 caracteres'})
        
        results = GlobalSearchService.search_all(query, request.user)
        
        # Formatar resultados para JSON
        formatted_results = []
        
        for projeto in results['projetos']:
            formatted_results.append({
                'type': 'projeto',
                'title': f"#{projeto.cod_projeto} - {projeto.nome}",
                'subtitle': f"Cliente: {projeto.cliente_nome}",
                'url': f'/projetos/{projeto.pk}/',
                'icon': 'fas fa-project-diagram'
            })
        
        for contrato in results['contratos']:
            formatted_results.append({
                'type': 'contrato',
                'title': f"{contrato.num_contrato} - {contrato.contratado}",
                'subtitle': f"Valor: R$ {contrato.valor}",
                'url': f'/contratos/{contrato.pk}/',
                'icon': 'fas fa-file-contract'
            })
        
        for usuario in results['usuarios']:
            formatted_results.append({
                'type': 'usuario',
                'title': usuario.get_full_name() or usuario.username,
                'subtitle': f"{usuario.email} - {usuario.get_role_display()}",
                'url': f'/accounts/users/{usuario.pk}/',
                'icon': 'fas fa-user'
            })
        
        return JsonResponse({
            'results': formatted_results,
            'total': len(formatted_results)
        })