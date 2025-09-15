"""
Management command para importar dados legados do arquivo inserts_postgres.sql
"""
import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.conf import settings


class Command(BaseCommand):
    help = 'Importa dados legados do arquivo inserts_postgres.sql'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='inserts_postgres.sql',
            help='Caminho para o arquivo SQL (padrão: inserts_postgres.sql no diretório raiz)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo teste sem aplicar mudanças'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        
        # Se não for caminho absoluto, assume que está na raiz do projeto
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Arquivo não encontrado: {file_path}')
            )
            return
        
        self.stdout.write(f'Lendo arquivo: {file_path}')
        self.stdout.write(f'Modo: {"DRY RUN" if dry_run else "EXECUÇÃO REAL"}')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao ler arquivo: {e}')
            )
            return
        
        # Divide o SQL em declarações individuais
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        self.stdout.write(f'Encontradas {len(statements)} declarações SQL')
        
        if dry_run:
            self.stdout.write('=== DRY RUN - Mostrando primeiras 5 declarações ===')
            for i, stmt in enumerate(statements[:5]):
                self.stdout.write(f'{i+1}. {stmt[:100]}...')
            if len(statements) > 5:
                self.stdout.write(f'... e mais {len(statements) - 5} declarações')
            return
        
        # Executa as declarações em uma transação
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    success_count = 0
                    error_count = 0
                    
                    for i, statement in enumerate(statements):
                        try:
                            cursor.execute(statement)
                            success_count += 1
                            if (i + 1) % 100 == 0:
                                self.stdout.write(f'Processadas {i + 1} declarações...')
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'Erro na declaração {i+1}: {e}')
                            )
                            # Continue com as próximas declarações
                            continue
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Importação concluída! '
                            f'Sucesso: {success_count}, Erros: {error_count}'
                        )
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante a importação: {e}')
            )