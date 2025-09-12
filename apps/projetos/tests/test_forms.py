from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from apps.projetos.forms.projeto_forms import ProjetoForm

User = get_user_model()

class ProjetoFormTest(TestCase):

    def setUp(self):
        self.responsavel = User.objects.create_user(username='testuser', email='test@user.com', password='12345')

    def test_projeto_form_valid(self):
        form_data = {
            'nome': 'Test Project',
            'data_inicio': date(2025, 1, 1),
            'data_encerramento': date(2025, 12, 31),
            'valor': 10000.00,
            'responsavel': self.responsavel.id,
            'cliente_nome': 'Test Client',
            'cliente_email': 'client@test.com',
            'situacao': '1',
        }
        form = ProjetoForm(data=form_data)
        self.assertTrue(form.is_valid())
