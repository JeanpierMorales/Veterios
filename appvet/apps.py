from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AppvetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appvet'

    def ready(self):
        post_migrate.connect(crear_admin_automatico, sender=self)


def crear_admin_automatico(sender, **kwargs):
    from django.contrib.auth.models import User

    admin_email = "admin@veterios.com"
    admin_pass = "Admin123*"
    admin_username = "admin"

    if not User.objects.filter(username=admin_username).exists():

        print("[SEEDING] Creando administrador...")

        admin_usuario = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_pass
        )

        admin_usuario.first_name = "Administrador"
        admin_usuario.save()