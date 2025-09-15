"""
Comando de gerenciamento para popular o banco de dados com dados do arquivo inserts_postgres.sql
"""
import re
import os
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

# Import models
from apps.projetos.models import Projeto
from apps.contratos.models import Contrato


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados do arquivo inserts_postgres.sql'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='inserts_postgres.sql',
            help='Caminho para o arquivo SQL (padrão: inserts_postgres.sql)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa os dados existentes antes de inserir novos'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_data = options['clear']
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Arquivo {file_path} não encontrado!')
            )
            return

        self.stdout.write(f'Lendo arquivo: {file_path}')
        
        # Limpar dados se solicitado
        if clear_data:
            self.clear_existing_data()

        # Processar arquivo SQL
        self.process_sql_file(file_path)
        
        self.stdout.write(
            self.style.SUCCESS('Population completa!')
        )

    def clear_existing_data(self):
        """Limpa dados existentes das tabelas"""
        self.stdout.write('Limpando dados existentes...')
        
        # Ordem de exclusão para respeitar FKs
        models_to_clear = [Projeto, Contrato]
        
        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'  - {model.__name__}: {count} registros removidos')

    def process_sql_file(self, file_path):
        """Processa o arquivo SQL e insere os dados"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Extrair e processar INSERT statements para projetos
        self.process_projetos_inserts(content)
        
        # Processar outros modelos se existirem
        self.process_contratos_inserts(content)

    def process_projetos_inserts(self, content):
        """Processa INSERTs da tabela projetos"""
        self.stdout.write('Processando projetos...')
        
        # Regex para capturar INSERT statements de projetos
        pattern = r"INSERT INTO projetos \([^)]+\) VALUES \(([^)]+)\);"
        matches = re.findall(pattern, content)
        
        projetos_to_create = []
        
        for match in matches:
            # Parse dos valores
            values = self.parse_sql_values(match)
            
            if len(values) >= 6:
                try:
                    projeto = Projeto(
                        cod_projeto=int(values[0]),
                        nome=values[1].strip("'"),
                        data_inicio=datetime.strptime(values[2].strip("'"), '%Y-%m-%d').date(),
                        data_encerramento=datetime.strptime(values[3].strip("'"), '%Y-%m-%d').date(),
                        valor=Decimal(values[4]),
                        situacao=values[5].strip("'")
                    )
                    projetos_to_create.append(projeto)
                except (ValueError, TypeError) as e:
                    self.stdout.write(
                        self.style.WARNING(f'Erro ao processar projeto: {values} - {e}')
                    )
                    continue
        
        # Bulk create em lotes
        if projetos_to_create:
            batch_size = 1000
            with transaction.atomic():
                for i in range(0, len(projetos_to_create), batch_size):
                    batch = projetos_to_create[i:i + batch_size]
                    Projeto.objects.bulk_create(batch, ignore_conflicts=True)
                    
            self.stdout.write(
                self.style.SUCCESS(f'  - {len(projetos_to_create)} projetos inseridos')
            )

    def process_contratos_inserts(self, content):
        """Processa INSERTs da tabela contrato"""
        self.stdout.write('Processando contratos...')
        
        # Regex para capturar INSERT statements de contrato
        pattern = r"INSERT INTO contrato \([^)]+\) VALUES \(([^)]+)\);"
        matches = re.findall(pattern, content)
        
        contratos_to_create = []
        
        for match in matches:
            # Parse dos valores
            values = self.parse_sql_values(match)
            
            if len(values) >= 3:  # Ajustar conforme estrutura real
                try:
                    # Ajustar campos conforme o modelo Contrato
                    contrato_data = {}
                    
                    # Mapear campos do SQL para o modelo Django
                    if len(values) > 0:
                        contrato_data['num_contrato'] = values[0].strip("'")
                    if len(values) > 1:
                        contrato_data['cod_ordem'] = int(values[1]) if values[1] != 'NULL' else None
                    if len(values) > 2:
                        contrato_data['descricao'] = values[2].strip("'") if values[2] != 'NULL' else ''
                    
                    contrato = Contrato(**contrato_data)
                    contratos_to_create.append(contrato)
                    
                except (ValueError, TypeError) as e:
                    self.stdout.write(
                        self.style.WARNING(f'Erro ao processar contrato: {values} - {e}')
                    )
                    continue
        
        # Bulk create em lotes
        if contratos_to_create:
            batch_size = 1000
            with transaction.atomic():
                for i in range(0, len(contratos_to_create), batch_size):
                    batch = contratos_to_create[i:i + batch_size]
                    Contrato.objects.bulk_create(batch, ignore_conflicts=True)
                    
            self.stdout.write(
                self.style.SUCCESS(f'  - {len(contratos_to_create)} contratos inseridos')
            )

    def parse_sql_values(self, values_string):
        """Parse dos valores de um INSERT SQL"""
        # Remove espaços em branco no início e fim
        values_string = values_string.strip()
        
        # Split por vírgulas mas respeitando strings entre aspas
        values = []
        current_value = ""
        in_quotes = False
        
        for char in values_string:
            if char == "'" and not in_quotes:
                in_quotes = True
                current_value += char
            elif char == "'" and in_quotes:
                in_quotes = False
                current_value += char
            elif char == "," and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char
        
        # Adicionar último valor
        if current_value.strip():
            values.append(current_value.strip())
        
        return values