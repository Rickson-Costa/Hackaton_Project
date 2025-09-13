# apps/contratos/views/pagamento_views.py
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db import models, transaction
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from datetime import timedelta

from ..models.item_contrato import ItemContrato
from ..models.contrato import Contrato
from ..forms.pagamento_forms import ItemContratoForm, RegistrarPagamentoForm


class ParcelaListView(LoginRequiredMixin, ListView):
    model = ItemContrato
    template_name = 'contratos/parcela_list.html'
    context_object_name = 'parcelas'
    paginate_by = 20

    def get_queryset(self):
        """Filtrar parcelas baseado nos parâmetros"""
        queryset = ItemContrato.objects.select_related(
            'num_contrato', 
            'num_contrato__cod_ordem',
            'num_contrato__cod_ordem__cod_requisicao',
            'num_contrato__cod_ordem__cod_requisicao__cod_projeto'
        ).order_by('data_vencimento', 'num_contrato__num_contrato', 'num_parcela')
        
        # Filtros
        status_filter = self.request.GET.get('status')
        search = self.request.GET.get('search')
        hoje = timezone.now().date()
        
        if status_filter == 'vencidas':
            queryset = queryset.filter(situacao='1', data_vencimento__lt=hoje)
        elif status_filter == 'hoje':
            queryset = queryset.filter(situacao='1', data_vencimento=hoje)
        elif status_filter == 'proximas':
            proxima_semana = hoje + timedelta(days=7)
            queryset = queryset.filter(
                situacao='1', 
                data_vencimento__gt=hoje,
                data_vencimento__lte=proxima_semana
            )
        elif status_filter == 'pagas':
            queryset = queryset.filter(situacao='3')
        
        if search:
            queryset = queryset.filter(
                Q(num_contrato__num_contrato__icontains=search) |
                Q(num_contrato__contratado__icontains=search) |
                Q(num_contrato__cpf_cnpj__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        proxima_semana = hoje + timedelta(days=7)
        
        # Resumo das parcelas
        all_parcelas = ItemContrato.objects.all()
        
        context['resumo'] = {
            'vencidas': all_parcelas.filter(situacao='1', data_vencimento__lt=hoje).count(),
            'hoje': all_parcelas.filter(situacao='1', data_vencimento=hoje).count(),
            'proximas': all_parcelas.filter(
                situacao='1', 
                data_vencimento__gt=hoje,
                data_vencimento__lte=proxima_semana
            ).count(),
            'pagas': all_parcelas.filter(situacao='3').count(),
            'valor_total': all_parcelas.aggregate(
                total=Sum('valor_parcela')
            )['total'] or 0,
        }
        
        context['today'] = hoje
        context['proxima_semana'] = proxima_semana
        context['current_filter'] = self.request.GET.get('status', 'todas')
        
        return context


class ItemContratoCreateView(LoginRequiredMixin, CreateView):
    model = ItemContrato
    form_class = ItemContratoForm
    template_name = 'contratos/itemcontrato_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.contrato = get_object_or_404(Contrato, pk=self.kwargs['contrato_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Gerar código de lançamento automaticamente
        ultimo_lancamento = self.contrato.itens.order_by('-cod_lancamento').first()
        cod_lancamento = (ultimo_lancamento.cod_lancamento + 1) if ultimo_lancamento else 1
        
        # Gerar número da parcela automaticamente
        ultima_parcela = self.contrato.itens.order_by('-num_parcela').first()
        num_parcela = (ultima_parcela.num_parcela + 1) if ultima_parcela else (self.contrato.parcelas + 1)
        
        form.instance.num_contrato = self.contrato
        form.instance.cod_lancamento = cod_lancamento
        form.instance.num_parcela = num_parcela
        form.instance.data_lancamento = timezone.now().date()
        
        messages.success(self.request, 'Parcela adicionada com sucesso!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('contratos:contrato_detail', kwargs={'pk': self.contrato.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contrato'] = self.contrato
        return context


class RegistrarPagamentoView(LoginRequiredMixin, View):
    """View para registrar pagamento de uma parcela"""
    
    def post(self, request, parcela_pk):
        parcela = get_object_or_404(ItemContrato, pk=parcela_pk)
        
        # Verificar se pode receber pagamento
        if not parcela.pode_receber_pagamento():
            messages.error(request, "Esta parcela não pode receber pagamentos.")
            return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)
        
        try:
            with transaction.atomic():
                # Obter dados do formulário
                valor_pago_str = request.POST.get('valor_pago')
                data_pagamento_str = request.POST.get('data_pagamento')
                observacoes = request.POST.get('observacoes', '')
                
                if not valor_pago_str:
                    messages.error(request, "O valor pago é obrigatório.")
                    return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)
                
                try:
                    valor_pago = float(valor_pago_str.replace(',', '.'))
                except (ValueError, AttributeError):
                    messages.error(request, "Valor pago inválido.")
                    return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)
                
                # Validar valor
                valor_pendente = float(parcela.get_valor_pendente())
                if valor_pago <= 0:
                    messages.error(request, "O valor pago deve ser maior que zero.")
                    return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)
                
                if valor_pago > valor_pendente:
                    messages.error(request, f"O valor pago não pode ser maior que o valor pendente (R$ {valor_pendente:.2f}).")
                    return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)
                
                # Registrar pagamento
                parcela.valor_pago += valor_pago
                
                # Definir data do pagamento
                if data_pagamento_str:
                    from datetime import datetime
                    parcela.data_pagamento = datetime.strptime(data_pagamento_str, '%Y-%m-%d').date()
                else:
                    parcela.data_pagamento = timezone.now().date()
                
                # Atualizar observações
                if observacoes:
                    if parcela.observacoes:
                        parcela.observacoes += f"\n---\n{observacoes}"
                    else:
                        parcela.observacoes = observacoes
                
                # Atualizar situação
                if parcela.valor_pago >= parcela.valor_parcela:
                    parcela.situacao = '3'  # Paga
                    parcela.valor_pago = parcela.valor_parcela  # Não deixar pagar a mais
                elif parcela.valor_pago > 0:
                    parcela.situacao = '4'  # Parcialmente Paga
                
                parcela.save()
                
                # Atualizar totais do contrato
                contrato = parcela.num_contrato
                contrato.atualizar_valores()
                
                messages.success(
                    request, 
                    f"Pagamento de R$ {valor_pago:.2f} registrado com sucesso! "
                    f"Parcela {parcela.num_parcela}/{contrato.parcelas} - {parcela.get_situacao_display()}."
                )
                
        except Exception as e:
            messages.error(request, f"Erro ao registrar pagamento: {str(e)}")
        
        return redirect('contratos:contrato_detail', pk=parcela.num_contrato.pk)


class PagamentoLoteView(LoginRequiredMixin, View):
    """View para pagamentos em lote"""
    
    def post(self, request):
        parcela_ids = request.POST.getlist('parcelas')
        
        if not parcela_ids:
            return JsonResponse({
                'success': False,
                'message': 'Nenhuma parcela selecionada.'
            })
        
        try:
            with transaction.atomic():
                parcelas_processadas = 0
                valor_total = 0
                
                for parcela_id in parcela_ids:
                    try:
                        parcela = ItemContrato.objects.get(pk=parcela_id)
                        
                        if parcela.pode_receber_pagamento():
                            valor_pendente = parcela.get_valor_pendente()
                            parcela.valor_pago = parcela.valor_parcela
                            parcela.situacao = '3'  # Paga
                            parcela.data_pagamento = timezone.now().date()
                            parcela.save()
                            
                            # Atualizar contrato
                            parcela.num_contrato.atualizar_valores()
                            
                            parcelas_processadas += 1
                            valor_total += float(valor_pendente)
                            
                    except ItemContrato.DoesNotExist:
                        continue
                
                return JsonResponse({
                    'success': True,
                    'message': f'{parcelas_processadas} parcela(s) paga(s) com sucesso! Total: R$ {valor_total:.2f}',
                    'processadas': parcelas_processadas,
                    'valor_total': valor_total
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao processar pagamentos: {str(e)}'
            })


class AdiarParcelasView(LoginRequiredMixin, View):
    """View para adiar vencimento de parcelas"""
    
    def post(self, request):
        parcela_ids = request.POST.getlist('parcelas')
        dias_str = request.POST.get('dias')
        
        if not parcela_ids:
            return JsonResponse({
                'success': False,
                'message': 'Nenhuma parcela selecionada.'
            })
        
        try:
            dias = int(dias_str)
            if dias <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Número de dias deve ser maior que zero.'
                })
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Número de dias inválido.'
            })
        
        try:
            with transaction.atomic():
                parcelas_adiadas = 0
                
                for parcela_id in parcela_ids:
                    try:
                        parcela = ItemContrato.objects.get(pk=parcela_id, situacao='1')
                        parcela.data_vencimento += timedelta(days=dias)
                        
                        # Adicionar observação
                        observacao = f"Vencimento adiado em {dias} dias em {timezone.now().date()}"
                        if parcela.observacoes:
                            parcela.observacoes += f"\n{observacao}"
                        else:
                            parcela.observacoes = observacao
                        
                        parcela.save()
                        parcelas_adiadas += 1
                        
                    except ItemContrato.DoesNotExist:
                        continue
                
                return JsonResponse({
                    'success': True,
                    'message': f'{parcelas_adiadas} parcela(s) adiada(s) por {dias} dias.',
                    'adiadas': parcelas_adiadas
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao adiar parcelas: {str(e)}'
            })


class ParcelaDetailAPIView(LoginRequiredMixin, View):
    """API para obter detalhes de uma parcela"""
    
    def get(self, request, parcela_id):
        try:
            parcela = ItemContrato.objects.select_related(
                'num_contrato',
                'num_contrato__cod_ordem',
                'num_contrato__cod_ordem__cod_requisicao',
                'num_contrato__cod_ordem__cod_requisicao__cod_projeto'
            ).get(pk=parcela_id)
            
            data = {
                'id': parcela.pk,
                'num_parcela': parcela.num_parcela,
                'valor_parcela': float(parcela.valor_parcela),
                'valor_pago': float(parcela.valor_pago),
                'valor_pendente': float(parcela.get_valor_pendente()),
                'data_vencimento': parcela.data_vencimento.strftime('%d/%m/%Y'),
                'data_pagamento': parcela.data_pagamento.strftime('%d/%m/%Y') if parcela.data_pagamento else None,
                'situacao': parcela.get_situacao_display(),
                'observacoes': parcela.observacoes,
                'contrato': {
                    'num_contrato': parcela.num_contrato.num_contrato,
                    'contratado': parcela.num_contrato.contratado,
                    'valor_total': float(parcela.num_contrato.valor),
                    'total_parcelas': parcela.num_contrato.parcelas,
                },
                'projeto': {
                    'nome': parcela.num_contrato.cod_ordem.cod_requisicao.cod_projeto.nome,
                    'codigo': parcela.num_contrato.cod_ordem.cod_requisicao.cod_projeto.cod_projeto,
                } if hasattr(parcela.num_contrato.cod_ordem, 'cod_requisicao') else None
            }
            
            return JsonResponse(data)
            
        except ItemContrato.DoesNotExist:
            return JsonResponse({
                'error': 'Parcela não encontrada.'
            }, status=404)


class RelatorioInadimplenciaView(LoginRequiredMixin, ListView):
    """Relatório de inadimplência"""
    model = ItemContrato
    template_name = 'contratos/relatorio_inadimplencia.html'
    context_object_name = 'parcelas_vencidas'
    
    def get_queryset(self):
        hoje = timezone.now().date()
        return ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__lt=hoje
        ).select_related('num_contrato').order_by('data_vencimento')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        
        # Classificar inadimplência por período
        inadimplencia = {
            '0-30': {'parcelas': [], 'valor': 0},
            '31-60': {'parcelas': [], 'valor': 0},
            '61-90': {'parcelas': [], 'valor': 0},
            '90+': {'parcelas': [], 'valor': 0}
        }
        
        for parcela in context['parcelas_vencidas']:
            dias_atraso = (hoje - parcela.data_vencimento).days
            valor_pendente = float(parcela.get_valor_pendente())
            
            if dias_atraso <= 30:
                periodo = '0-30'
            elif dias_atraso <= 60:
                periodo = '31-60'
            elif dias_atraso <= 90:
                periodo = '61-90'
            else:
                periodo = '90+'
            
            inadimplencia[periodo]['parcelas'].append(parcela)
            inadimplencia[periodo]['valor'] += valor_pendente
        
        context['inadimplencia'] = inadimplencia
        context['valor_total_vencido'] = sum(p['valor'] for p in inadimplencia.values())
        
        return context