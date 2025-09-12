from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.projetos.models.projeto import Projeto
from datetime import date

User = get_user_model()

class ProjetoViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@user.com', password='12345')
        self.client.login(username='testuser', password='12345')
        self.responsavel = self.user
        self.projeto = Projeto.objects.create(
            nome='Test Project',
            data_inicio=date(2025, 1, 1),
            data_encerramento=date(2025, 12, 31),
            valor=10000.00,
            responsavel=self.responsavel,
            cliente_nome='Test Client',
            cliente_email='client@test.com',
        )

    def test_projeto_list_view(self):
        response = self.client.get(reverse('projetos:projeto_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
