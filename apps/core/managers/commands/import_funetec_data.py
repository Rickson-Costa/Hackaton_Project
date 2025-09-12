# apps/core/management/commands/import_funetec_data.py
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from decimal import Decimal
from apps.projetos.models import Projeto, Requisicao, Ordem, ItemOrdem
from apps.contratos.models import Contrato, ItemContrato

class Command(BaseCommand):
    help = 'Importa dados dos arquivos Excel do FUNETEC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='data/',
            help='Caminho para os arquivos Excel'
        )

    def handle(self, *args, **options):
        path = options['path']
        
        with transaction.atomic():
            self.stdout.write('Iniciando importação dos dados FUNETEC...')
            
            # 1. Importar Projetos
            self.import_projetos(f'{path}tb_projetos.xlsx')
            
            # 2. Importar Requisições
            self.import_requisicoes(f'{path}tb_requisicao.xlsx')
            
            # 3. Importar Ordens
            self.import_ordens(f'{path}tb_ordem.xlsx')
            
            # 4. Importar Itens da Ordem
            self.import_itens_ordem(f'{path}tb_itens_ordem.xlsx')
            
            # 5. Importar Contratos
            self.import_contratos(f'{path}tb_contratos.xlsx')
            
            # 6. Importar Itens do Contrato
            self.import_itens_contrato(f'{path}tb_itens_contrato.xlsx')
            
            self.stdout.write(self.style.SUCCESS('Importação concluída com sucesso!'))

    def import_projetos(self, filepath):
        self.stdout.write('Importando projetos...')
        df = pd.read_excel(filepath)
        
        for _, row in df.iterrows():
            Projeto.objects.update_or_create(
                cod_projeto=int(row['codProjeto']),
                defaults={
                    'nome': row['nome'],
                    'data_inicio': pd.to_datetime(row['dataInicio']).date(),
                    'data_encerramento': pd.to_datetime(row['dataEncerramento']).date(),
                    'valor': Decimal(str(row['valor'])),
                    'situacao': str(row['situacao']),
                }
            )
        
        self.stdout.write(f'  ✓ {len(df)} projetos importados')

    def import_requisicoes(self, filepath):
        self.stdout.write('Importando requisições...')
        df = pd.read_excel(filepath)
        
        for _, row in df.iterrows():
            try:
                projeto = Projeto.objects.get(cod_projeto=int(row['codProjeto']))
                Requisicao.objects.update_or_create(
                    cod_requisicao=int(row['codRequisicao']),
                    defaults={
                        'cod_projeto': projeto,
                        'descricao': row['descricao'],
                        'data_solicitacao': pd.to_datetime(row['dataSolicitacao']).date(),
                        'data_limite': pd.to_datetime(row['dataLimite']).date(),
                        'valor': Decimal(str(row['valor'])),
                        'situacao': str(row['situacao']),
                    }
                )
            except Projeto.DoesNotExist:
                self.stdout.write(f'  ⚠ Projeto {row["codProjeto"]} não encontrado')
        
        self.stdout.write(f'  ✓ {len(df)} requisições importadas')

    def import_ordens(self, filepath):
        self.stdout.write('Importando ordens de serviço...')
        df = pd.read_excel(filepath)
        
        for _, row in df.iterrows():
            try:
                requisicao = Requisicao.objects.get(cod_requisicao=int(row['codRequisicao']))
                Ordem.objects.update_or_create(
                    cod_ordem=int(row['codOrdem']),
                    defaults={
                        'cod_requisicao': requisicao,
                        'descricao': row['descricao'],
                        'data_solicitacao': pd.to_datetime(row['dataSolicitacao']).date(),
                        'data_limite': pd.to_datetime(row['dataLimite']).date(),
                        'valor': Decimal(str(row['valor'])),
                        'situacao': str(row['situacao']),
                    }
                )
            except Requisicao.DoesNotExist:
                self.stdout.write(f'  ⚠ Requisição {row["codRequisicao"]} não encontrada')
        
        self.stdout.write(f'  ✓ {len(df)} ordens importadas')

    def import_itens_ordem(self, filepath):
        self.stdout.write('Importando itens da ordem...')
        df = pd.read_excel(filepath)
        
        for _, row in df.iterrows():
            try:
                ordem = Ordem.objects.get(cod_ordem=int(row['codOrdem']))
                ItemOrdem.objects.update_or_create(
                    cod_ordem=ordem,
                    cod_item=int(row['codItem']),
                    defaults={
                        'descricao': row['descricao'],
                        'data_solicitacao': pd.to_datetime(row['dataSolicitacao']).date(),
                        'data_limite': pd.to_datetime(row['dataLimite']).date(),
                        'valor': Decimal(str(row['valor'])),
                        'data_recebido': pd.to_datetime(row['dataRecebido']).date() if pd.notna(row['dataRecebido']) else None,
                        'situacao': str(row['situacao']),
                    }
                )
            except Ordem.DoesNotExist:
                self.stdout.write(f'  ⚠ Ordem {row["codOrdem"]} não encontrada')
        
        self.stdout.write(f'  ✓ {len(df)} itens de ordem importados')

    def import_contratos(self, filepath):
        self.stdout.write('Importando contratos...')
        df = pd.read_excel(filepath)
        
        for _, row in df.iterrows():
            try:
                ordem = Ordem.objects.get(cod_ordem=int(row['codOrdem']))
                Contrato.objects.update_or_create(
                    num_contrato=row['numContrato'],
                    defaults={
                        'cod_ordem': ordem,
                        'descricao': row['descricao'],
                        'cpf_cnpj': str(row['cpfcnpj']),
                        'contratado': row['contratado'],
                        'tipo_pessoa': int(row['tipoPessoa']),
                        'data_inicio': pd.to_datetime(row['dataInicio']).date(),
                        'data_fim': pd.to_datetime(row['dataFim']).date(),
                        'valor': Decimal(str(row['valor'])),
                        'parcelas': int(row['parcelas']),
                        'data_parcela_inicial': pd.to_datetime(row['dataParcelaInicial']).date(),
                        'situacao': str(row['situacao']),
                    }
                )
            except Ordem.DoesNotExist:
                self.stdout.write(f'  ⚠ Ordem {row["codOrdem"]} não encontrada')
        
        self.stdout.write(f'  ✓ {len(df)} contratos importados')

    def import_itens_contrato(self, filepath):
        self.stdout.write('Importando itens de contrato (parcelas)...')
        df = pd.read_excel(filepath)
        
        for _, row in df.iterrows():
            try:
                contrato = Contrato.objects.get(num_contrato=row['numContrato'])
                ItemContrato.objects.update_or_create(
                    num_contrato=contrato,
                    cod_lancamento=int(row['codLancamento']),
                    defaults={
                        'data_lancamento': pd.to_datetime(row['dataLancamento']).date(),
                        'num_parcela': int(row['numParcela']),
                        'valor_parcela': Decimal(str(row['valorParcela'])),
                        'data_vencimento': pd.to_datetime(row['dataVencimento']).date(),
                        'valor_pago': Decimal(str(row['valorPago'])),
                        'data_pagamento': pd.to_datetime(row['dataPagamento']).date() if pd.notna(row['dataPagamento']) else None,
                        'situacao': str(row['situacao']),
                    }
                )
            except Contrato.DoesNotExist:
                self.stdout.write(f'  ⚠ Contrato {row["numContrato"]} não encontrado')
        
        self.stdout.write(f'  ✓ {len(df)} parcelas importadas')