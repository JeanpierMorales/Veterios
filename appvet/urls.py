from django.urls import path
from . import views


urlpatterns = [
    # Al entrar a la web, cargamos Quienes Somos por defecto
    path('', views.quienes_somos, name='index'), 
    
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('ofertas/', views.ofertas, name='ofertas'),
    path('login/', views.login_view, name='login'),
    

    # ESTAS SON LAS QUE FALTAN:
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),


    



    # ===============================================================
    # CONTROL DE RUTAS SUITE DE ADMINISTRACIÓN (MÁXIMA PRIORIDAD)
    # ===============================================================
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/gestion-citas/', views.gestion_citas, name='gestion_citas'),
    path('admin/asignar-veterinario/', views.asignar_veterinario, name='asignar_veterinario'),
    path('admin/eliminar-cita/<int:id>/', views.eliminar_cita, name='eliminar_cita'),
    
    path('admin/lista-veterinarios/', views.lista_veterinarios, name='lista_veterinarios'),
    path('admin/registrar-veterinario/', views.registrar_veterinario, name='registrar_veterinario'),
    path('admin/cambiar-estado-veterinario/', views.cambiar_estado_veterinario, name='cambiar_estado_veterinario'),
    
    path('admin/seguimientos/', views.pacientes_porvolver, name='pacientes_porvolver'),
    path('admin/preparar-seguimiento/<int:mascota_id>/', views.preparar_cita_seguimiento, name='preparar_cita_seguimiento'),
    path('admin/guardar-seguimiento/', views.guardar_cita_seguimiento, name='guardar_cita_seguimiento'),


















    # 2. Ruta Veterinario (La que agregamos para el nuevo rol)
    path(
        'veterinario/inicio/',
        views.veterinario_inicio,
        name='veterinario_inicio'
    ),
    path(
        'veterinario/historial/',
        views.historial_pacientes,
        name='historial_pacientes'
    ),
    path(
        'veterinario/mis-consultas/',
        views.mis_consultas,
        name='mis_consultas'
    ),
    path(
        'veterinario/paciente/<int:id>/',
        views.detalle_paciente,
        name='detalle_paciente'
    ),
    path(
        'veterinario/finalizar-consulta/<int:cita_id>/',
        views.finalizar_consulta,
        name='finalizar_consulta'
    ),

    # 3. Ruta Cliente
    path('inicio/', views.inicio_cliente_view, name='inicio_cliente'),
    path('cliente/mis-mascotas/', views.mis_mascotas, name='mis_mascotas'),
    path('cliente/agregar-mascota/', views.agregar_mascota, name='agregar_mascota'),
    path('cliente/registrar-mascota/', views.registrar_mascota, name='registrar_mascota'),
    
    # Rutas de Solicitud de Citas (Hacen match con tus action)
    path('cliente/solicitar/', views.solicitar_cita, name='cliente_solicitar'),
    path('cliente/guardar-cita/', views.guardar_cita, name='guardar_cita'),
    path('cliente/solicitar-cita/', views.solicitar_cita, name='solicitar_cita'), # Parche de seguridad para los fronts cruzados
    
    # Rutas de Paneles
    path('cliente/citas/', views.cliente_citas, name='cliente_citas'),
    path('cliente/historial/', views.cliente_historial, name='cliente_historial'),
    
    # Gestión de Cuenta e Identity
    path('cliente/configuracion/', views.cliente_configuracion, name='cliente_configuracion'),
    path('cliente/actualizar-configuracion/', views.actualizar_configuracion, name='actualizar_configuracion'),
    path('cliente/cambiar-password/', views.cambiar_password, name='cambiar_password'),


    

]

