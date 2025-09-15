// static/js/dashboard.js

class DashboardManager {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        this.isUpdating = false;
        
        // Configurações dos gráficos
        this.chartDefaults = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupTooltips();
        this.loadWidgets();
    }
    
    setupEventListeners() {
        // Refresh automático
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.refreshData();
            }
        });
        
        // Cliques em cards de métricas
        document.querySelectorAll('.metric-card').forEach(card => {
            card.addEventListener('click', this.handleMetricCardClick.bind(this));
        });
        
        // Filtros e ordenação
        document.querySelectorAll('[data-filter]').forEach(filter => {
            filter.addEventListener('change', this.handleFilterChange.bind(this));
        });
    }
    
    setupTooltips() {
        // Inicializar tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Inicializar gráficos
    initCharts(config) {
        this.initEvolucaoFinanceiraChart(config.evolucao_financeira);
        this.initProjetosSituacaoChart(config.projetos_por_situacao);
        this.initStatusChart(config.status_projetos);
    }
    
    initEvolucaoFinanceiraChart(data) {
        const ctx = document.getElementById('chartEvolucaoFinanceira');
        if (!ctx) return;
        
        this.charts.evolucaoFinanceira = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                ...this.chartDefaults,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': R$ ' + 
                                       context.parsed.y.toLocaleString('pt-BR');
                            }
                        }
                    }
                },
                elements: {
                    line: {
                        tension: 0.1
                    },
                    point: {
                        radius: 4,
                        hoverRadius: 6
                    }
                }
            }
        });
    }
    
    initProjetosSituacaoChart(data) {
        const ctx = document.getElementById('chartProjetosSituacao');
        if (!ctx) return;
        
        this.charts.projetosSituacao = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                ...this.chartDefaults,
                cutout: '60%',
                plugins: {
                    ...this.chartDefaults.plugins,
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
    
    initStatusChart(data) {
        // Gráfico de status usando Chart.js ou elementos customizados
        this.updateStatusIndicators(data);
    }
    
    updateStatusIndicators(data) {
        const indicators = document.querySelectorAll('.status-indicator h4');
        if (indicators.length >= 4) {
            indicators[0].textContent = data.verde;
            indicators[1].textContent = data.amarelo;
            indicators[2].textContent = data.vermelho;
            indicators[3].textContent = data.total;
        }
        
        // Animação de contagem
        this.animateCounters();
    }
    
    animateCounters() {
        document.querySelectorAll('.status-indicator h4').forEach(counter => {
            const target = parseInt(counter.textContent);
            const duration = 1000; // 1 segundo
            const increment = target / (duration / 16); // 60 FPS
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = target;
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current);
                }
            }, 16);
        });
    }
    
    // Atualizar dados via AJAX
    async refreshData() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        this.showLoadingState();
        
        try {
            const response = await fetch(window.location.href + '?ajax=1', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error('Erro na requisição');
            
            const data = await response.json();
            this.updateDashboard(data);
            this.showSuccessMessage('Dashboard atualizado com sucesso');
            
        } catch (error) {
            console.error('Erro ao atualizar dashboard:', error);
            this.showErrorMessage('Erro ao atualizar dados');
        } finally {
            this.isUpdating = false;
            this.hideLoadingState();
        }
    }
    
    updateDashboard(data) {
        // Atualizar métricas
        this.updateMetrics(data.metricas_projetos, data.metricas_contratos, data.metricas_financeiras);
        
        // Atualizar gráficos
        this.updateCharts(data.graficos_config);
        
        // Atualizar tabelas
        this.updateTables(data.projetos_recentes, data.parcelas_vencimento);
        
        // Atualizar alertas
        this.updateAlerts(data.alertas);
    }
    
    updateMetrics(projetos, contratos, financeiras) {
        // Atualizar cards de métricas
        const metricsMap = {
            'projetos-total': projetos.total,
            'projetos-andamento': projetos.em_andamento,
            'projetos-percentual': projetos.percentual_realizado + '%',
            'contratos-total': contratos.total,
            'contratos-ativos': contratos.ativos,
            'contratos-percentual': contratos.percentual_pago + '%',
            'receita-total': this.formatCurrency(contratos.valor_total),
            'receita-pendente': this.formatCurrency(contratos.valor_pendente),
            'parcelas-vencidas': financeiras.parcelas_vencidas,
            'valor-vencido': this.formatCurrency(financeiras.valor_vencido)
        };
        
        Object.entries(metricsMap).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateValueChange(element, value);
            }
        });
    }
    
    updateCharts(config) {
        // Atualizar gráficos existentes
        if (this.charts.evolucaoFinanceira) {
            this.charts.evolucaoFinanceira.data = config.evolucao_financeira;
            this.charts.evolucaoFinanceira.update('active');
        }
        
        if (this.charts.projetosSituacao) {
            this.charts.projetosSituacao.data = config.projetos_por_situacao;
            this.charts.projetosSituacao.update('active');
        }
        
        this.updateStatusIndicators(config.status_projetos);
    }
    
    animateValueChange(element, newValue) {
        element.style.transform = 'scale(1.1)';
        element.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            element.textContent = newValue;
            element.style.transform = 'scale(1)';
        }, 100);
    }
    
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }
    
    // Estados de loading
    showLoadingState() {
        document.body.classList.add('loading');
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Atualizando...';
            refreshBtn.disabled = true;
        }
    }
    
    hideLoadingState() {
        document.body.classList.remove('loading');
        const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i>Atualizar';
            refreshBtn.disabled = false;
        }
    }
    
    // Mensagens de feedback
    showSuccessMessage(message) {
        this.showToast(message, 'success');
    }
    
    showErrorMessage(message) {
        this.showToast(message, 'error');
    }
    
    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Container para toasts
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
        bsToast.show();
        
        // Remover do DOM após ocultar
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    // Widgets dinâmicos
    loadWidgets() {
        this.loadSidebarAlerts();
        this.loadQuickStats();
    }
    
    async loadSidebarAlerts() {
        try {
            const response = await fetch('/dashboard/widget/alertas/');
            const html = await response.text();
            const alertsContainer = document.getElementById('sidebar-alerts');
            if (alertsContainer) {
                alertsContainer.innerHTML = html;
                alertsContainer.classList.add('fade-in');
            }
        } catch (error) {
            console.error('Erro ao carregar alertas:', error);
        }
    }
    
    // Manipuladores de eventos
    handleMetricCardClick(event) {
        const card = event.currentTarget;
        const metric = card.dataset.metric;
        
        // Navegação baseada no tipo de métrica
        const routes = {
            'projetos': '/projetos/',
            'contratos': '/contratos/',
            'financeiro': '/dashboard/analytics/financeiro/',
            'parcelas': '/contratos/parcelas/all/'
        };
        
        if (routes[metric]) {
            window.location.href = routes[metric];
        }
    }
    
    handleFilterChange(event) {
        const filter = event.target;
        const filterType = filter.dataset.filter;
        const value = filter.value;
        
        // Aplicar filtro baseado no tipo
        this.applyFilter(filterType, value);
    }
    
    applyFilter(type, value) {
        const tables = document.querySelectorAll('table tbody tr');
        
        tables.forEach(row => {
            const shouldShow = this.evaluateFilterCondition(row, type, value);
            row.style.display = shouldShow ? '' : 'none';
        });
    }
    
    evaluateFilterCondition(row, type, value) {
        if (value === '' || value === 'all') return true;
        
        const cells = row.querySelectorAll('td');
        
        switch (type) {
            case 'status':
                const statusBadge = cells[2]?.querySelector('.badge');
                return statusBadge?.textContent.toLowerCase().includes(value.toLowerCase());
                
            case 'prazo':
                const prazoBadge = cells[3]?.querySelector('.badge');
                return prazoBadge?.classList.contains(`bg-${value}`);
                
            default:
                return true;
        }
    }
    
    // Exportação de dados
    exportData(format, type) {
        const url = `/relatorios/${type}/${format}/`;
        window.open(url, '_blank');
    }
    
    // Impressão de relatórios
    printDashboard() {
        window.print();
    }
    
    // Cleanup
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
}

// Funções globais para manter compatibilidade
let dashboardManager;

function initDashboardCharts(config) {
    dashboardManager = new DashboardManager();
    dashboardManager.initCharts(config);
}

function refreshDashboard() {
    if (dashboardManager) {
        dashboardManager.refreshData();
    } else {
        location.reload();
    }
}

function updateDashboardMetrics(data) {
    if (dashboardManager) {
        dashboardManager.updateDashboard(data);
    }
}

function updateCharts(config) {
    if (dashboardManager) {
        dashboardManager.updateCharts(config);
    }
}

// Utilitários para AJAX
class AjaxManager {
    static async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('Erro na requisição AJAX:', error);
            throw error;
        }
    }
    
    static async get(url, params = {}) {
        const urlWithParams = new URL(url, window.location.origin);
        Object.entries(params).forEach(([key, value]) => {
            urlWithParams.searchParams.append(key, value);
        });
        
        return this.request(urlWithParams.toString());
    }
    
    static async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        });
    }
    
    static getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Configurações globais do Chart.js
    Chart.defaults.font.family = 'inherit';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    
    // Estilo para impressão
    const printStyles = `
        @media print {
            .sidebar, .navbar, .btn, .dropdown { display: none !important; }
            .col-md-9.ms-sm-auto.col-lg-10 { margin: 0 !important; width: 100% !important; }
            .card { break-inside: avoid; margin-bottom: 1rem; }
            .chart-area, .chart-pie { height: 300px !important; }
        }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = printStyles;
    document.head.appendChild(styleSheet);
});

// Cleanup ao sair da página
window.addEventListener('beforeunload', function() {
    if (dashboardManager) {
        dashboardManager.destroy();
    }
});