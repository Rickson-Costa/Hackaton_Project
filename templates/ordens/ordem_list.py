{% extends 'base/base.html' %}

{% block title %}Lista de Ordens - FUNETEC{% endblock %}
{% block page_title %}Ordens de Serviço{% endblock %}

{% block content %}
<div class="card shadow-sm">
    <div class="card-header">
        <h5 class="mb-0">Ordens da Requisição #{{ requisicao.cod_requisicao }}</h5>
    </div>
    <div class="card-body">
        <a href="{% url 'projetos:ordem_create' requisicao.pk %}" class="btn btn-primary mb-3">
            <i class="fas fa-plus me-1"></i> Nova Ordem
        </a>
        
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Código</th>
                        <th>Descrição</th>
                        <th>Valor</th>
                        <th>Data Limite</th>
                        <th>Situação</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for ordem in ordens %}
                    <tr>
                        <td><strong>#{{ ordem.cod_ordem }}</strong></td>
                        <td>{{ ordem.descricao|truncatechars:50 }}</td>
                        <td>R$ {{ ordem.valor|floatformat:2 }}</td>
                        <td>{{ ordem.data_limite|date:"d/m/Y" }}</td>
                        <td><span class="badge bg-info">{{ ordem.get_situacao_display }}</span></td>
                        <td>
                            <a href="{% url 'projetos:ordem_detail' ordem.pk %}" class="btn btn-sm btn-outline-info">
                                <i class="fas fa-eye"></i>
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="6" class="text-center text-muted">Nenhuma ordem encontrada.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}