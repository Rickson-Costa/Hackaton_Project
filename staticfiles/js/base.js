// static/js/base.js

class BaseSystem {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupTooltips();
        this.setupConfirmations();
        this.setupFormValidations();
        this.setupAjaxSetup();
    }
    
    setupTooltips() {
        // Inicializar tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    setupConfirmations() {
        // Confirmações para ações destrutivas
        document.addEventListener('click', function(e) {
            const target = e.target.closest('[data-confirm]');
            if (target) {
                e.preventDefault();
                const message = target.dataset.confirm || 'Tem certeza?';
                if (confirm(message)) {
                    if (target.href) {
                        window.location.href = target.href;
                    } else if (target.closest('form')) {
                        target.closest('form').submit();
                    }
                }
            }
        });
    }
    
    setupFormValidations() {
        // Validação básica de formulários
        const forms = document.querySelectorAll('.needs-validation');
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }
    
    setupAjaxSetup() {
        // Configuração CSRF para AJAX
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            window.csrfToken = csrfToken;
        }
    }
    
    showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }
    
    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }
    
    formatDate(date) {
        return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
    }
    
    // Utility para requisições AJAX
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': window.csrfToken || '',
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
            console.error('Erro na requisição:', error);
            this.showToast('Erro na requisição: ' + error.message, 'error');
            throw error;
        }
    }
}

// Funções globais utilitárias
window.BaseSystem = BaseSystem;

// Inicializar quando DOM carregar
document.addEventListener('DOMContentLoaded', function() {
    window.baseSystem = new BaseSystem();
    
    // Auto-dismiss alerts após 5 segundos
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Funções helper globais
function showToast(message, type = 'info') {
    if (window.baseSystem) {
        window.baseSystem.showToast(message, type);
    }
}

function formatCurrency(value) {
    if (window.baseSystem) {
        return window.baseSystem.formatCurrency(value);
    }
    return `R$ ${value}`;
}

function formatDate(date) {
    if (window.baseSystem) {
        return window.baseSystem.formatDate(date);
    }
    return date;
}