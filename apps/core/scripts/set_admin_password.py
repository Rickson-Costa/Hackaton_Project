from django.contrib.auth import get_user_model

User = get_user_model()

def run():
    try:
        user = User.objects.get(username='admin')
        user.set_password('admin123456')
        user.save()
        print("Senha do admin alterada com sucesso.")
    except User.DoesNotExist:
        print("Usuário admin não encontrado.")
