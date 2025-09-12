{% extends 'base/base.html' %}

{% block title %}Lista de Requisições - FUNETEC{% endblock %}
{% block page_title %}Requisições do Projeto{% endblock %}

{% block content %}
<div class="card shadow-sm">
    <div class="card-header">
        <h5 class="mb-0">Requisições do Projeto: {{ projeto.nome }}</h5>
    </div>
    <div class="card-body">
        <a href="{% url 'projetos:requisicao_create' projeto.pk %}" class="btn btn-primary mb-3">
            <i class="fas fa-plus me-1"></i> Nova Requisição
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
                    {% for requisicao in requisicoes %}
                    <tr>
                        <td><strong>#{{ requisicao.cod_requisicao }}</strong></td>
                        <td>{{ requisicao.descricao|truncatechars:50 }}</td>
                        <td>R$ {{ requisicao.valor|floatformat:2 }}</td>
                        <td>{{ requisicao.data_limite|date:"d/m/Y" }}</td>
                        <td><span class="badge bg-info">{{ requisicao.get_situacao_display }}</span></td>
                        <td>
                            <a href="{% url 'projetos:requisicao_detail' requisicao.pk %}" class="btn btn-sm btn-outline-info">
                                <i class="fas fa-eye"></i>
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="6" class="text-center text-muted">Nenhuma requisição encontrada.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}