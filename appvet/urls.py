from django.urls import path
from . import views

urlpatterns = [
    # Rutas Públicas
    path('', views.home, name='home'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('ofertas/', views.ofertas, name='ofertas'),

    # Rutas de Admin
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/gestion-citas/', views.gestion_citas, name='gestion_citas'),
    path('admin/veterinarios/', views.lista_veterinarios, name='lista_veterinarios'),
    path('admin/pacientes-por-volver/', views.pacientes_por_volver, name='pacientes_porvolver'),

    # Acciones (POST)
    path('admin/asignar-veterinario/', views.asignar_veterinario, name='asignar_veterinario'),
    path('admin/eliminar-cita/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
]