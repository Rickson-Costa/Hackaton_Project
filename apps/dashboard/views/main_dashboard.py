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
        
        # ====== MÉTRICAS DE PROJETOS ======
        projetos = Projeto.objects.all()
        context['metricas_projetos'] = {
            'total': projetos.count(),
            'em_andamento': projetos.filter(situacao='2').count(),
            'atrasados': projetos.filter(
                situacao__in=['1', '2'],
                data_encerramento__lt=hoje
            ).count(),
            'concluidos': projetos.filter(situacao='6').count(),
            'valor_total': projetos.aggregate(Sum('valor'))['valor__sum'] or 0,
        }
        
        # ====== MÉTRICAS DE CONTRATOS ======
        contratos = Contrato.objects.all()
        contratos_pf = contratos.filter(tipo_pessoa=1)
        contratos_pj = contratos.filter(tipo_pessoa=2)
        
        context['metricas_contratos'] = {
            'total': contratos.count(),
            'pessoa_fisica': contratos_pf.count(),
            'pessoa_juridica': contratos_pj.count(),
            'valor_total': contratos.aggregate(Sum('valor'))['valor__sum'] or 0,
        }
        
        # ====== ANÁLISE DE INADIMPLÊNCIA ======
        parcelas_vencidas = ItemContrato.objects.filter(
            situacao='1',  # Lançado (não pago)
            data_vencimento__lt=hoje
        )
        
        inadimplencia = {
            '0-30': {'count': 0, 'valor': Decimal('0')},
            '31-60': {'count': 0, 'valor': Decimal('0')},
            '61-90': {'count': 0, 'valor': Decimal('0')},
            '90+': {'count': 0, 'valor': Decimal('0')},
        }
        
        for parcela in parcelas_vencidas:
            dias_atraso = (hoje - parcela.data_vencimento).days
            valor_pendente = parcela.valor_parcela - parcela.valor_pago
            
            if dias_atraso <= 30:
                periodo = '0-30'
            elif dias_atraso <= 60:
                periodo = '31-60'
            elif dias_atraso <= 90:
                periodo = '61-90'
            else:
                periodo = '90+'
            
            inadimplencia[periodo]['count'] += 1
            inadimplencia[periodo]['valor'] += valor_pendente
        
        context['inadimplencia'] = inadimplencia
        
        # ====== SEMÁFOROS (PRAZO, CUSTO, ESCOPO) ======
        semaforos = []
        
        for projeto in projetos.filter(situacao__in=['1', '2']):
            # Análise de Prazo
            dias_restantes = (projeto.data_encerramento - hoje).days
            dias_totais = (projeto.data_encerramento - projeto.data_inicio).days
            percentual_prazo = ((dias_totais - dias_restantes) / dias_totais * 100) if dias_totais > 0 else 0
            
            if dias_restantes < 0:
                status_prazo = 'vermelho'
            elif dias_restantes <= 7:
                status_prazo = 'amarelo'
            else:
                status_prazo = 'verde'
            
            # Análise de Custo (usando valor realizado)
            if hasattr(projeto, 'valor_realizado'):
                percentual_custo = (projeto.valor_realizado / projeto.valor * 100) if projeto.valor > 0 else 0
                if percentual_custo > 100:
                    status_custo = 'vermelho'
                elif percentual_custo > 90:
                    status_custo = 'amarelo'
                else:
                    status_custo = 'verde'
            else:
                status_custo = 'verde'
            
            # Análise de Escopo (baseado nas requisições)
            total_requisicoes = projeto.requisicoes.count()
            requisicoes_concluidas = projeto.requisicoes.filter(situacao='5').count()
            percentual_escopo = (requisicoes_concluidas / total_requisicoes * 100) if total_requisicoes > 0 else 0
            
            if percentual_escopo < 50 and percentual_prazo > 70:
                status_escopo = 'vermelho'
            elif percentual_escopo < 70 and percentual_prazo > 50:
                status_escopo = 'amarelo'
            else:
                status_escopo = 'verde'
            
            semaforos.append({
                'projeto': projeto,
                'prazo': status_prazo,
                'custo': status_custo,
                'escopo': status_escopo,
                'dias_restantes': dias_restantes,
                'percentual_custo': percentual_custo,
                'percentual_escopo': percentual_escopo,
            })
        
        context['semaforos'] = semaforos
        
        # ====== ALERTAS CRÍTICOS ======
        alertas = []
        
        # Projetos atrasados
        for projeto in projetos.filter(situacao__in=['1', '2'], data_encerramento__lt=hoje):
            dias_atraso = (hoje - projeto.data_encerramento).days
            alertas.append({
                'tipo': 'danger',
                'titulo': f'Projeto #{projeto.cod_projeto} - ATRASADO',
                'mensagem': f'{projeto.nome} - {dias_atraso} dias de atraso',
                'icone': 'exclamation-triangle'
            })
        
        # Parcelas vencidas há mais de 30 dias
        for parcela in parcelas_vencidas.filter(data_vencimento__lt=hoje - timedelta(days=30)):
            dias_atraso = (hoje - parcela.data_vencimento).days
            alertas.append({
                'tipo': 'warning',
                'titulo': f'Parcela Vencida - {parcela.num_contrato.contratado}',
                'mensagem': f'R$ {parcela.valor_parcela} - {dias_atraso} dias de atraso',
                'icone': 'dollar-sign'
            })
        
        # Ordens próximas do vencimento
        for ordem in Ordem.objects.filter(
            situacao__in=['1', '2'],
            data_limite__lte=hoje + timedelta(days=3),
            data_limite__gte=hoje
        ):
            dias_restantes = (ordem.data_limite - hoje).days
            alertas.append({
                'tipo': 'info',
                'titulo': f'OS #{ordem.cod_ordem} - Prazo Próximo',
                'mensagem': f'{ordem.descricao[:50]} - {dias_restantes} dias restantes',
                'icone': 'clock'
            })
        
        context['alertas'] = alertas[:10]  # Limitar a 10 alertas
        
        # ====== DADOS PARA GRÁFICOS ======
        
        # Gráfico de Situação dos Projetos
        situacao_projetos = projetos.values('situacao').annotate(count=Count('cod_projeto'))
        context['grafico_situacao_projetos'] = {
            'labels': [dict(Projeto.SITUACAO_CHOICES).get(s['situacao'], s['situacao']) for s in situacao_projetos],
            'data': [s['count'] for s in situacao_projetos]
        }
        
        # Gráfico Previsto vs Realizado (últimos 6 meses)
        meses = []
        valores_previstos = []
        valores_realizados = []
        
        for i in range(6):
            mes = hoje - timedelta(days=30*i)
            meses.insert(0, mes.strftime('%b/%Y'))
            
            # Valor previsto (soma dos contratos do mês)
            contratos_mes = Contrato.objects.filter(
                data_inicio__year=mes.year,
                data_inicio__month=mes.month
            )
            valor_previsto = contratos_mes.aggregate(Sum('valor'))['valor__sum'] or 0
            valores_previstos.insert(0, float(valor_previsto))
            
            # Valor realizado (soma dos pagamentos do mês)
            pagamentos_mes = ItemContrato.objects.filter(
                data_pagamento__year=mes.year,
                data_pagamento__month=mes.month
            )
            valor_realizado = pagamentos_mes.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
            valores_realizados.insert(0, float(valor_realizado))
        
        context['grafico_previsto_realizado'] = {
            'labels': meses,
            'previsto': valores_previstos,
            'realizado': valores_realizados
        }
        
        # ====== TOP 5 PRESTADORES ======
        top_prestadores = (
            Contrato.objects
            .values('contratado', 'cpf_cnpj', 'tipo_pessoa')
            .annotate(
                total_contratos=Count('num_contrato'),
                valor_total=Sum('valor')
            )
            .order_by('-valor_total')[:5]
        )
        context['top_prestadores'] = top_prestadores
        
        # ====== PRÓXIMAS PARCELAS A VENCER ======
        proximas_parcelas = ItemContrato.objects.filter(
            situacao='1',
            data_vencimento__gte=hoje,
            data_vencimento__lte=hoje + timedelta(days=30)
        ).select_related('num_contrato').order_by('data_vencimento')[:10]
        
        context['proximas_parcelas'] = proximas_parcelas
        
        return context