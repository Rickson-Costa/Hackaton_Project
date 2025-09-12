# apps/relatorios/services/report_service.py
import io
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from apps.projetos.models.projeto import Projeto

class ReportService:
    """
    Service para gerar relatórios em diferentes formatos.
    Implementa o padrão Factory Method.
    """
    def generate_report(self, format_type, queryset):
        if format_type == 'excel':
            return self._generate_excel(queryset)
        elif format_type == 'pdf':
            return self._generate_pdf(queryset)
        else:
            raise ValueError("Formato de relatório não suportado")

    def _generate_excel(self, queryset):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="relatorio_projetos.xlsx"'
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Projetos"

        # Cabeçalho
        columns = ['Código', 'Nome', 'Responsável', 'Situação', 'Valor Orçado']
        ws.append(columns)

        # Dados
        for projeto in queryset:
            row = [
                projeto.codProjeto,
                projeto.nome,
                projeto.responsavel.get_full_name(),
                projeto.get_situacao_display(),
                projeto.valor,
            ]
            ws.append(row)
        
        wb.save(response)
        return response

    def _generate_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_projetos.pdf"'

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        p.drawString(inch, 10.5 * inch, "Relatório de Projetos - FUNETEC")
        
        y = 10 * inch
        for projeto in queryset:
            text = f"#{projeto.codProjeto} - {projeto.nome} (Valor: R$ {projeto.valor})"
            p.drawString(inch, y, text)
            y -= 0.25 * inch
            if y < inch: # Page break
                p.showPage()
                y = 10.5 * inch

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response