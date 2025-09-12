# apps/dashboard/views/main_dashboard.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.projetos.models import Projeto, Requisicao, Ordem
from apps.contratos.models import Contrato, ItemContrato

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        
        # ====== MÉTRICAS PRINCIPAIS (KPIs) ======
        projetos = Projeto.objects.all()
        contratos = Contrato.objects.all()
        contratos_pf = contratos.filter(tipo_pessoa=1)
        contratos_pj = contratos.filter(tipo_pessoa=2)
        
        # Projetos
        projetos_ativos = projetos.filter(situacao='2').count()
        projetos_atrasados = projetos.filter(
            situacao__in=['1', '2'],
            data_encerramento__lt=hoje
        ).count()
        
        # Contratos PF
        contratos_pf_ativos = contratos_pf.filter(situacao__in=['1', '2']).count()
        contratos_pf_pendentes = ItemContrato.objects.filter(
            num_contrato__tipo_pessoa=1,
            situacao='1'
        ).count()
        
        # Contratos PJ
        contratos_pj_ativos = contratos_pj.filter(situacao__in=['1', '2']).count()
        contratos_pj_vencidos = contratos_pj.filter(
            data_fim__lt=hoje,
            situacao='2'
        ).count()
        
        # Inadimplência Total
        parcelas_vencidas = ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__lt=hoje
        )
        valor_inadimplencia = sum(
            (parcela.valor_parcela - parcela.valor_pago) 
            for parcela in parcelas_vencidas
        )
        valor_total_contratos = contratos.aggregate(Sum('valor'))['valor__sum'] or 1
        percentual_inadimplencia = (valor_inadimplencia / valor_total_contratos * 100) if valor_total_contratos > 0 else 0
        
        context['kpis'] = {
            'projetos_ativos': projetos_ativos,
            'projetos_crescimento': self._calcular_crescimento_projetos(),
            'contratos_pf_total': contratos_pf.count(),
            'contratos_pf_ativos': contratos_pf_ativos,
            'contratos_pf_pendentes': contratos_pf_pendentes,
            'contratos_pj_total': contratos_pj.count(),
            'contratos_pj_ativos': contratos_pj_ativos,
            'contratos_pj_vencidos': contratos_pj_vencidos,
            'valor_inadimplencia': float(valor_inadimplencia),
            'percentual_inadimplencia': float(percentual_inadimplencia),
        }
        
        # ====== GRÁFICO PREVISTO VS REALIZADO ======
        meses_labels = []
        valores_previstos = []
        valores_realizados = []
        
        for i in range(6):
            mes = hoje - timedelta(days=30*i)
            meses_labels.insert(0, mes.strftime('%b'))
            
            # Valores dos contratos do mês
            contratos_mes = Contrato.objects.filter(
                data_inicio__year=mes.year,
                data_inicio__month=mes.month
            )
            previsto = contratos_mes.aggregate(Sum('valor'))['valor__sum'] or 0
            valores_previstos.insert(0, float(previsto))
            
            # Pagamentos realizados no mês
            pagamentos_mes = ItemContrato.objects.filter(
                data_pagamento__year=mes.year,
                data_pagamento__month=mes.month
            )
            realizado = pagamentos_mes.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
            valores_realizados.insert(0, float(realizado))
        
        context['grafico_previsto_realizado'] = {
            'labels': meses_labels,
            'previsto': valores_previstos,
            'realizado': valores_realizados,
        }
        
        # ====== GRÁFICO STATUS DOS PROJETOS ======
        status_counts = projetos.values('situacao').annotate(count=Count('cod_projeto'))
        
        status_map = {
            '1': 'Aguardando',
            '2': 'Em Andamento',
            '3': 'Paralisado',
            '4': 'Suspenso',
            '5': 'Cancelado',
            '6': 'Concluído'
        }
        
        labels = []
        data = []
        for item in status_counts:
            labels.append(status_map.get(item['situacao'], item['situacao']))
            data.append(item['count'])
        
        context['grafico_status_projetos'] = {
            'labels': labels,
            'data': data,
        }
        
        # ====== GRÁFICO VENCIMENTOS ======
        vencimentos_data = []
        vencimentos_labels = ['Hoje', 'Amanhã', '3 dias', '7 dias', '15 dias', '30 dias']
        periodos = [0, 1, 3, 7, 15, 30]
        
        for dias in periodos:
            data_check = hoje + timedelta(days=dias)
            count = ItemContrato.objects.filter(
                situacao='1',
                data_vencimento=data_check
            ).count()
            vencimentos_data.append(count)
        
        context['grafico_vencimentos'] = {
            'labels': vencimentos_labels,
            'data': vencimentos_data,
        }
        
        # ====== ALERTAS CRÍTICOS ======
        alertas = []
        
        # Projetos com prazo crítico (vence em 7 dias ou menos)
        projetos_criticos = projetos.filter(
            situacao__in=['1', '2'],
            data_encerramento__lte=hoje + timedelta(days=7),
            data_encerramento__gte=hoje
        )
        
        for projeto in projetos_criticos[:3]:
            dias_restantes = (projeto.data_encerramento - hoje).days
            alertas.append({
                'tipo': 'danger' if dias_restantes <= 2 else 'warning',
                'titulo': f'Projeto #{projeto.cod_projeto} - Prazo Crítico',
                'mensagem': f'{projeto.nome[:30]} - Vence em {dias_restantes} dias',
                'tempo': 'Agora'
            })
        
        # Parcelas vencidas
        for parcela in parcelas_vencidas[:3]:
            dias_atraso = (hoje - parcela.data_vencimento).days
            alertas.append({
                'tipo': 'warning',
                'titulo': f'Contrato {parcela.num_contrato.num_contrato} - Parcela Vencida',
                'mensagem': f'R$ {parcela.valor_parcela} - {dias_atraso} dias de atraso',
                'tempo': 'Hoje'
            })
        
        # Orçamentos estourados
        projetos_estourados = projetos.filter(
            valor_realizado__gt=F('valor')
        )[:2]
        
        for projeto in projetos_estourados:
            percentual = (projeto.valor_realizado / projeto.valor * 100) if projeto.valor > 0 else 0
            alertas.append({
                'tipo': 'info',
                'titulo': 'Orçamento Estourado',
                'mensagem': f'Projeto #{projeto.cod_projeto} - {percentual:.0f}% do orçamento utilizado',
                'tempo': 'Ontem'
            })
        
        context['alertas'] = alertas
        
        # ====== TABELA DE PROJETOS CRÍTICOS ======
        projetos_tabela = []
        
        for projeto in projetos.filter(situacao__in=['1', '2'])[:5]:
            # Status Prazo
            if projeto.data_encerramento < hoje:
                status_prazo = 'red'
                prazo_texto = 'Atrasado'
            elif (projeto.data_encerramento - hoje).days <= 7:
                status_prazo = 'yellow'
                prazo_texto = 'Próximo'
            else:
                status_prazo = 'green'
                prazo_texto = 'No Prazo'
            
            # Status Custo
            if hasattr(projeto, 'custo_realizado') and projeto.custo_previsto > 0:
                percentual_custo = (projeto.custo_realizado / projeto.custo_previsto * 100)
                if percentual_custo > 100:
                    status_custo = 'red'
                elif percentual_custo > 90:
                    status_custo = 'yellow'
                else:
                    status_custo = 'green'
                custo_texto = f'{percentual_custo:.0f}%'
            else:
                status_custo = 'green'
                custo_texto = 'OK'
            
            projetos_tabela.append({
                'codigo': projeto.cod_projeto,
                'nome': projeto.nome[:30],
                'cliente': projeto.cliente_nome[:20] if hasattr(projeto, 'cliente_nome') else 'N/A',
                'status_prazo': status_prazo,
                'prazo_texto': prazo_texto,
                'status_custo': status_custo,
                'custo_texto': custo_texto,
                'status_geral': projeto.get_situacao_display(),
            })
        
        context['projetos_tabela'] = projetos_tabela
        
        return context
    
    def _calcular_crescimento_projetos(self):
        """Calcula crescimento percentual de projetos no mês"""
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
        
        projetos_mes_atual = Projeto.objects.filter(
            created_at__gte=inicio_mes
        ).count()
        
        projetos_mes_anterior = Projeto.objects.filter(
            created_at__gte=mes_anterior,
            created_at__lt=inicio_mes
        ).count()
        
        if projetos_mes_anterior > 0:
            crescimento = ((projetos_mes_atual - projetos_mes_anterior) / projetos_mes_anterior * 100)
            return round(crescimento, 1)
        return 0