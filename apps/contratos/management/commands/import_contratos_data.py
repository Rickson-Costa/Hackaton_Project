# apps/contratos/management/commands/import_contratos_data.py
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from decimal import Decimal
from apps.contratos.models import Contrato, ItemContrato
from apps.projetos.models import Ordem

class Command(BaseCommand):
    help = 'Importa dados dos contratos e parcelas dos arquivos Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--contratos-file',
            type=str,
            required=True,
            help='Caminho para o arquivo Excel de contratos'
        )
        parser.add_argument(
            '--parcelas-file',
            type=str,
            required=True,
            help='Caminho para o arquivo Excel de parcelas'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Atualizar registros existentes'
        )

    def handle(self, *args, **options):
        contratos_file = options['contratos_file']
        parcelas_file = options['parcelas_file']
        update_existing = options['update']
        
        self.stdout.write('Iniciando importação dos contratos...')
        
        try:
            with transaction.atomic():
                # Importar contratos
                contratos_criados = self.import_contratos(contratos_file, update_existing)
                
                # Importar parcelas
                parcelas_criadas = self.import_parcelas(parcelas_file, update_existing)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Importação concluída com sucesso!\n'
                        f'Contratos: {contratos_criados}\n'
                        f'Parcelas: {parcelas_criadas}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante a importação: {str(e)}')
            )
            raise

    def import_contratos(self, filepath, update_existing):
        """Importa contratos do arquivo Excel"""
        self.stdout.write('Importando contratos...')
        
        df = pd.read_excel(filepath)
        contratos_criados = 0
        contratos_atualizados = 0
        
        for _, row in df.iterrows():
            try:
                # Buscar ordem de serviço
                try:
                    ordem = Ordem.objects.get(cod_ordem=int(row['codOrdem']))
                except Ordem.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Ordem {row['codOrdem']} não encontrada para contrato {row['numContrato']}"
                        )
                    )
                    continue
                
                # Dados do contrato
                contrato_data = {
                    'cod_ordem': ordem,
                    'descricao': row['objeto'],
                    'cpf_cnpj': str(row['cpfCnpj']).replace('.', '').replace('-', '').replace('/', ''),
                    'contratado': row['contratado'],
                    'tipo_pessoa': int(row['tipoPessoa']),
                    'data_inicio': pd.to_datetime(row['dataInicio']).date(),
                    'data_fim': pd.to_datetime(row['dataFim']).date(),
                    'valor': Decimal(str(row['valor'])),
                    'parcelas': int(row['parcelas']),
                    'data_parcela_inicial': pd.to_datetime(row['dataParcelaInicial']).date(),
                    'situacao': str(row['situacao']),
                }
                
                # Criar ou atualizar contrato
                contrato, created = Contrato.objects.update_or_create(
                    num_contrato=row['numContrato'],
                    defaults=contrato_data
                )
                
                if created:
                    contratos_criados += 1
                    self.stdout.write(f"  ✓ Contrato {contrato.num_contrato} criado")
                elif update_existing:
                    contratos_atualizados += 1
                    self.stdout.write(f"  ↻ Contrato {contrato.num_contrato} atualizado")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Erro ao processar contrato {row['numContrato']}: {str(e)}"
                    )
                )
                continue
        
        self.stdout.write(
            f"Contratos processados: {contratos_criados} criados, {contratos_atualizados} atualizados"
        )
        return contratos_criados

    def import_parcelas(self, filepath, update_existing):
        """Importa parcelas/itens de contrato do arquivo Excel"""
        self.stdout.write('Importando parcelas...')
        
        df = pd.read_excel(filepath)
        parcelas_criadas = 0
        parcelas_atualizadas = 0
        
        for _, row in df.iterrows():
            try:
                # Buscar contrato
                try:
                    contrato = Contrato.objects.get(num_contrato=row['numContrato'])
                except Contrato.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Contrato {row['numContrato']} não encontrado para parcela {row['codLancamento']}"
                        )
                    )
                    continue
                
                # Dados da parcela
                parcela_data = {
                    'num_contrato': contrato,
                    'data_lancamento': pd.to_datetime(row['dataLancamento']).date(),
                    'num_parcela': int(row['numParcela']),
                    'valor_parcela': Decimal(str(row['valorParcela'])),
                    'data_vencimento': pd.to_datetime(row['dataVencimento']).date(),
                    'valor_pago': Decimal(str(row['valorPago'])) if pd.notna(row['valorPago']) else Decimal('0'),
                    'data_pagamento': (
                        pd.to_datetime(row['dataPagamento']).date() 
                        if pd.notna(row['dataPagamento']) else None
                    ),
                    'situacao': str(row['situacao']),
                    'observacoes': str(row.get('observacoes', '')) if pd.notna(row.get('observacoes')) else '',
                }
                
                # Criar ou atualizar parcela
                parcela, created = ItemContrato.objects.update_or_create(
                    num_contrato=contrato,
                    cod_lancamento=int(row['codLancamento']),
                    defaults=parcela_data
                )
                
                if created:
                    parcelas_criadas += 1
                elif update_existing:
                    parcelas_atualizadas += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Erro ao processar parcela {row['numContrato']}/{row['codLancamento']}: {str(e)}"
                    )
                )
                continue
        
        self.stdout.write(
            f"Parcelas processadas: {parcelas_criadas} criadas, {parcelas_atualizadas} atualizadas"
        )
        return parcelas_criadas

    def validar_dados(self, df, required_columns):
        """Valida se o DataFrame tem as colunas necessárias"""
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Colunas obrigatórias ausentes: {missing_columns}")
        return True