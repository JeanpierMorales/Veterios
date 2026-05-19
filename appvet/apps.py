from django.apps import AppConfig
from django.db.models.signals import post_migrate

def crear_admin_automatico(sender, **kwargs):
    """
    Equivalente al Seeding de Identity en Program.cs.
    Crea el rol de administrador y el usuario si no existen.
    """
    from django.contrib.auth.models import User
    
    # Configuramos las credenciales por defecto (puedes cambiarlas)
    admin_email = "admin@veterios.com"
    admin_pass = "Admin123*"
    admin_username = "admin"

    # Verificamos si ya existe en MySQL
    if not User.objects.filter(username=admin_username).exists():
        print(" [SEEDING] Creando cuenta de Administrador automática...")
        
        # is_staff e is_superuser le dan rango administrativo total de Django
        admin_usuario = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_pass
        )
        # Forzamos los accesos por si acaso
        admin_usuario.is_staff = True
        admin_usuario.is_superuser = True
        admin_usuario.first_name = "Administrador"
        admin_usuario.save()

class AppvetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appvet'

    