from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from apps.projetos.models.projeto import Projeto

User = get_user_model()

class ProjetoModelTest(TestCase):

    def setUp(self):
        self.responsavel = User.objects.create_user(username='testuser', email='test@user.com', password='12345')
        self.projeto = Projeto.objects.create(
            nome='Test Project',
            data_inicio=date(2025, 1, 1),
            data_encerramento=date(2025, 12, 31),
            valor=10000.00,
            responsavel=self.responsavel,
            cliente_nome='Test Client',
            cliente_email='client@test.com',
        )

    def test_projeto_creation(self):
        self.assertIsInstance(self.projeto, Projeto)
        self.assertEqual(self.projeto.nome, 'Test Project')
