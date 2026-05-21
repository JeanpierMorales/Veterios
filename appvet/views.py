from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import Mascota, Cita, Veterinario, HistoriaClinica
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import connection
from datetime import date, datetime
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from datetime import date, datetime, timedelta


# ==========================================
# VISTAS PÚBLICAS 
# ==========================================

def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('username')
        contrasena = request.POST.get('password')
        
        username_real = login_input
        
        if '@' in login_input:
            try:
                usuario_obj = User.objects.get(email=login_input)
                username_real = usuario_obj.username
            except User.DoesNotExist:
                username_real = login_input

        user = authenticate(request, username=username_real, password=contrasena)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"¡Bienvenido, {user.first_name or user.username}!")
            
            # REDIRECCIONES CORRECTAS POR URL ABSOLUTA
            if user.is_superuser or user.is_staff:
                return redirect('/admin/dashboard/')  # Fuerza ir al panel admin
            
            elif Veterinario.objects.filter(usuario_id=user.username).exists():
                return redirect('/veterinario/inicio/')  # Fuerza ir al panel médico
            
            else:
                return redirect('/inicio/')  # Fuerza ir al espacio del cliente
                
        else:
            messages.error(request, "El correo electrónico o la contraseña son incorrectos.")
            
    return render(request, 'appvet/account/login.html')




def quienes_somos(request):
    # Esta es tu página de aterrizaje principal
    return render(request, 'appvet/account/quienes_somos.html')

def ofertas(request):
    return render(request, 'appvet/account/ofertas.html')



def register_view(request):
    if request.method == 'POST':
        nombre_completo = request.POST.get('username')
        correo = request.POST.get('email')
        contrasena = request.POST.get('password')
        
        if User.objects.filter(email=correo).exists():
            messages.error(request, "Este correo electrónico ya se encuentra registrado.", extra_tags='register')
            return redirect('login')
            
        try:
            username_unico = correo.split('@')[0]
            if User.objects.filter(username=username_unico).exists():
                username_unico = f"{username_unico}_{User.objects.count()}"
                
            nuevo_usuario = User.objects.create_user(
                username=username_unico, 
                email=correo, 
                password=contrasena
            )
            nuevo_usuario.first_name = nombre_completo
            nuevo_usuario.save()
            
            auth_login(request, nuevo_usuario)
            messages.success(request, "¡Tu cuenta ha sido creada con éxito! Bienvenido a VETERIOS.")
            
            # Al registrarse, es un cliente nuevo, va directo a su espacio de inicio
            return redirect('/inicio/')
            
        except Exception as e:
            messages.error(request, f"Hubo un problema al crear la cuenta: {str(e)}", extra_tags='register')
            return redirect('login')
            
    return redirect('login')





def logout_view(request):
    auth_logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('quienes_somos')


# ==========================================
# VISTAS DE ADMINISTRADOR
# ==========================================

@staff_member_required(login_url='login')
def dashboard_admin(request):
    hoy = date.today()
    
    # Equivalente a tus CountAsync() de Entity Framework
    citas_hoy = Cita.objects.filter(fecha=hoy).count()
    citas_pendientes = Cita.objects.filter(estado="Pendiente").count()
    total_mascotas = Mascota.objects.count()
    
    context = {
        'citas_hoy': citas_hoy,
        'citas_pendientes': citas_pendientes,
        'total_mascotas': total_mascotas,
        'db_online': True, # Si carga la vista, la conexión a MySQL está activa
        'app_activa': True
    }
    return render(request, 'appvet/admin/dashboard_admin.html', context)


@staff_member_required(login_url='login')
def gestion_citas(request):
    # .all().order_by('-fecha') es el equivalente a tu ToListAsync() con OrderByDescending
    citas = Cita.objects.all().order_by('-fecha')
    veterinarios = Veterinario.objects.filter(esta_activo=True)
    
    context = {
        'citas': citas,
        'veterinarios': veterinarios
    }
    return render(request, 'appvet/admin/gestion_citas.html', context)


@staff_member_required(login_url='login')
def asignar_veterinario(request):
    if request.method == 'POST':
        cita_id = request.POST.get('cita_id')
        veterinario_id = request.POST.get('veterinario_id')
        
        cita_actual = get_object_or_404(Cita, id=cita_id)
        
        # SEGURIDAD: Si ya está completada, no permitir cambios
        if cita_actual.estado == "Completada":
            messages.error(request, "No se puede cambiar el médico de una cita que ya ha sido completada.")
            return redirect('gestion_citas')
            
        # VALIDACIÓN DE CHOQUE DE HORARIOS (Igual a tu AnyAsync de C#)
        esta_ocupado = Cita.objects.filter(
            veterinario_id=veterinario_id,
            fecha=cita_actual.fecha,
            horario=cita_actual.horario
        ).exclude(id=cita_id).exclude(estado="Cancelada").exists()
        
        if esta_ocupado:
            messages.error(request, f"Asignación fallida: El médico ya tiene un turno ocupado a las {cita_actual.horario}")
            return redirect('gestion_citas')
            
        vet = get_object_or_404(Veterinario, id=veterinario_id)
        cita_actual.veterinario = vet
        cita_actual.nombre_veterinario = vet.nombre
        cita_actual.estado = "Confirmada"
        cita_actual.save()
        
        messages.success(request, "Asignación actualizada correctamente.")
    return redirect('gestion_citas')


@staff_member_required(login_url='login')
def eliminar_cita(request, id):
    if request.method == 'POST':
        # 1. Buscamos e instalamos remoción en cascada para historias clínicas asociadas
        HistoriaClinica.objects.filter(cita_id=id).delete()
        
        # 2. Ahora sí borramos la cita de MySQL
        cita = get_object_or_404(Cita, id=id)
        cita.delete()
        
    return redirect('gestion_citas')


@staff_member_required(login_url='login')
def lista_veterinarios(request):
    vete = Veterinario.objects.all()
    context = {
        'veterinarios': vete
    }
    return render(request, 'appvet/admin/lista_veterinarios.html', context)


@staff_member_required(login_url='login')
def registrar_veterinario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        especialidad = request.POST.get('especialidad')
        
        if nombre and especialidad:
            # Reemplaza espacios y pasa a minúsculas para emular tu lógica de C#
            email_acceso = nombre.replace(" ", "").lower() + "@veterios.com"
            username_acceso = nombre.replace(" ", "").lower()
            
            # Verificamos si no existe ya el usuario en auth_user
            if not User.objects.filter(username=username_acceso).exists():
                # Equivalente a resultadoIdentity = await _userManager.CreateAsync(...)
                nuevo_usuario = User.objects.create_user(
                    username=username_acceso,
                    email=email_acceso,
                    password="Veterios2026*" # Clave por defecto encriptada
                )
                nuevo_usuario.first_name = nombre
                nuevo_usuario.save()
                
                # Registramos en tu tabla de perfiles 'Veterinario'
                vete = Veterinario.objects.create(
                    nombre=nombre,
                    especialidad=especialidad,
                    usuario_id=nuevo_usuario.username, # Se enlaza con el ID o Username de tu modelo
                    esta_activo=True
                )
                
                # Usamos extra_tags para que tu SweetAlert del HTML se dispare solo
                messages.success(request, "Se asignó tu veterinario con éxito", extra_tags='registro_exitoso')
                
    return redirect('lista_veterinarios')


@staff_member_required(login_url='login')
def cambiar_estado_veterinario(request):
    if request.method == 'POST':
        vet_id = request.POST.get('id')
        vet = get_object_or_404(Veterinario, id=vet_id)
        vet.esta_activo = not vet.esta_activo
        vet.save()
    return redirect('lista_veterinarios')


@staff_member_required(login_url='login')
def pacientes_porvolver(request):
    # Buscamos historias clínicas que tengan una fecha sugerida asignada por el médico
    sugerencias = HistoriaClinica.objects.filter(proxima_cita_sugerida__isnull=False).order_by('proxima_cita_sugerida')
    context = {
        'historias': sugerencias
    }
    return render(request, 'appvet/admin/pacientes_porvolver.html', context)


@staff_member_required(login_url='login')
def preparar_cita_seguimiento(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    fecha_sugerida = request.GET.get('fecha', date.today().strftime('%Y-%m-%d'))
    
    context = {
        'mascota_id': mascota.id,
        'nombre_mascota': mascota.nombre,
        'fecha_sugerida': fecha_sugerida,
        'usuario_id': mascota.usuario_id,
        'veterinarios': Veterinario.objects.filter(esta_activo=True),
        'fecha_actual': date.today().strftime('%Y-%m-%d')
    }
    return render(request, 'appvet/admin/crearcita_seguimiento.html', context)


@staff_member_required(login_url='login')
def guardar_cita_seguimiento(request):
    if request.method == 'POST':
        mascota_id = request.POST.get('MascotaId')
        veterinario_id = request.POST.get('VeterinarioId')
        fecha_str = request.POST.get('Fecha')
        horario = request.POST.get('Horario')
        servicio = request.POST.get('Servicio')
        prioridad = request.POST.get('Prioridad')
        
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        # Validar Choque de Horario (Doctor ocupado)
        esta_ocupado = Cita.objects.filter(
            veterinario_id=veterinario_id,
            fecha=fecha_obj,
            horario=horario
        ).exclude(estado="Cancelada").exists()
        
        if esta_ocupado:
            messages.error(request, f"El médico ya tiene una cita asignada para esa fecha a las {horario}.")
            return redirect('pacientes_porvolver')
            
        vet = get_object_or_404(Veterinario, id=veterinario_id)
        mascota = get_object_or_404(Mascota, id=mascota_id)
        
        # Guardamos la nueva cita de control preventivo
        Cita.objects.create(
            mascota=mascota,
            veterinario=vet,
            nombre_veterinario=vet.nombre,
            fecha=fecha_obj,
            horario=horario,
            servicio=servicio,
            prioridad=prioridad,
            estado="Confirmada"
        )
        
        # Limpiar el seguimiento anterior (poner en NULL para que no vuelva a figurar en la lista)
        historia_anterior = HistoriaClinica.objects.filter(
            mascota_id=mascota_id, 
            proxima_cita_sugerida__isnull=False
        ).order_by('-fecha_atencion').first()
        
        if historia_anterior:
            historia_anterior.proxima_cita_sugerida = None
            historia_anterior.save()
            
        messages.success(request, "Cita de seguimiento agendada con éxito.")
    return redirect('gestion_citas')

@staff_member_required(login_url='login')
def ver_expediente(request, mascota_id):
    # 1. Traemos la mascota específica con sus datos y su dueño
    mascota = get_object_or_404(Mascota.objects.select_related('usuario'), id=mascota_id)
    
    # 2. Traemos TODAS las atenciones médicas que ha tenido esta mascota en su vida
    atenciones_pasadas = HistoriaClinica.objects.filter(mascota_id=mascota_id).order_by('-fecha_atencion')
    
    context = {
        'mascota': mascota,
        'atenciones': atenciones_pasadas
    }
    return render(request, 'appvet/veterinario/ver_expediente.html', context)























































# ===============================================================
# PORTAL DEL CLIENTE
# ===============================================================

@login_required(login_url='login')
def inicio_cliente_view(request):
    hoy = date.today()
    
    # 1. Jalamos las mascotas del usuario logueado (Equivalente a tu .Where(m => m.UsuarioId == userId))
    mascotas = Mascota.objects.filter(usuario=request.user)
    
    # 2. Traemos las citas médicas del cliente programadas para hoy ordenadas por horario
    citas_hoy = Cita.objects.filter(
        mascota__usuario=request.user, 
        fecha=hoy
    ).order_by('horario')

# 3. Traer el historial médico real (¡ESTO ES LO QUE BUSCA TU TABLA DE ABAJO!)
    historial_medico = HistoriaClinica.objects.filter(
        mascota__usuario=request.user
    ).order_by('-fecha_atencion')  # De la más reciente a la más antigua

    context = {
        'title': 'Inicio',  # <-- Mantiene el título para el header_cliente.html
        'mascotas': mascotas,
        'total_mascotas': mascotas.count(),
        'citas_hoy': citas_hoy,
        'historial_medico': historial_medico
    }
    return render(request, 'appvet/cliente/inicio_cliente.html', context)


@login_required(login_url='login')
def agregar_mascota(request):
    # Pasamos el title para mantener consistente la interfaz
    return render(request, 'appvet/cliente/agregar_mascota.html', {'title': 'Agregar Mascota'})

@login_required(login_url='login')
def registrar_mascota(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        especie = request.POST.get('especie')
        raza = request.POST.get('raza')
        
        # --- AGREGA ESTOS CAMPOS FALTANTES ---
        sexo = request.POST.get('sexo')  # Captura lo que envíe el select/input
        fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
        
        # Procesar la fecha si viene del formulario, si no, usar la de hoy
        fecha_nacimiento_obj = date.today()
        if fecha_nacimiento_str:
            try:
                fecha_nacimiento_obj = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            except ValueError:
                fecha_nacimiento_obj = date.today()

        # Guardamos la nueva mascota con el set completo de datos
        Mascota.objects.create(
            nombre=nombre,
            especie=especie,
            raza=raza,
            sexo=sexo,  # <-- Ahora sí se guarda en MySQL
            fecha_nacimiento=fecha_nacimiento_obj,  # <-- Se guarda la fecha real
            usuario=request.user
        )
        return redirect('inicio_cliente')
        
    return redirect('agregar_mascota')

@login_required(login_url='login')
def mis_mascotas(request):
    mascotas = Mascota.objects.filter(usuario=request.user)
    return render(request, 'appvet/cliente/mis_mascotas.html', {'mascotas': mascotas})


@login_required(login_url='login')
def solicitar_cita(request):
    # Cargamos el combo-box del formulario con las mascotas del usuario logueado
    mascotas = Mascota.objects.filter(usuario=request.user)
    return render(request, 'appvet/cliente/solicitar.html', {'mascotas': mascotas})


@login_required(login_url='login')
def guardar_cita(request):
    # SOLUCIÓN: Importamos 'messages' al inicio de la función para que esté disponible en todo el bloque
    from django.contrib import messages
    
    if request.method == 'POST':
        mascota_id = request.POST.get('mascota_id')
        servicio = request.POST.get('servicio')
        horario = request.POST.get('horario')
        fecha_str = request.POST.get('fecha')
        
        if not mascota_id or not servicio or not horario or not fecha_str:
            messages.error(request, "Por favor, complete todos los campos obligatorios.")
            return redirect('cliente_solicitar')
            
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            mascota_sel = get_object_or_404(Mascota, id=mascota_id, usuario=request.user)
            
            # Creación limpia en la base de datos MySQL
            Cita.objects.create(
                mascota=mascota_sel,
                servicio=servicio,
                fecha=fecha_obj,
                horario=horario,
                estado="Pendiente"
            )
            
            # Ahora funcionará perfecto porque 'messages' ya está definido globalmente en la función
            messages.success(request, "Tu cita ha sido registrada exitosamente.")
            return redirect('cliente_citas')
            
        except Exception as e:
            print(f"Error al insertar cita: {e}")
            messages.error(request, "No se pudo registrar la cita. Verifique los datos.")
            return redirect('cliente_solicitar')
            
    return redirect('cliente_solicitar')


@login_required(login_url='login')
def cliente_citas(request):
    # Equivalente a tu .Include(c => c.Mascota).OrderByDescending(c => c.Fecha)
    citas = Cita.objects.filter(mascota__usuario=request.user).order_by('-fecha')
    return render(request, 'appvet/cliente/citas.html', {'citas': citas})


@login_required(login_url='login')
def cliente_historial(request):
    """
    Trae las citas completadas del cliente logueado junto con su diagnóstico y tratamiento
    """
    # Buscamos las citas completadas o canceladas del usuario actual
    # Traemos 'mascota', 'veterinario' y pre-cargamos la historia clínica asociada
    citas_completadas = Cita.objects.select_related(
        'mascota', 
        'veterinario'
    ).prefetch_related(
        'historias_clinicas'  
    ).filter(
        mascota__usuario=request.user,
        estado__in=['Completada', 'Cancelada']
    ).order_by('-fecha')

    # Inyectamos el diagnóstico y tratamiento en caliente a cada cita
    for cita in citas_completadas:
        # Obtenemos la primera historia clínica asociada a esta cita (si existe)
        historia = cita.historias_clinicas.first()
        if historia:
            cita.diagnostico_txt = historia.diagnostico
            cita.tratamiento_txt = historia.tratamiento
        else:
            cita.diagnostico_txt = "Sin diagnóstico registrado en la atención."
            cita.tratamiento_txt = "Sin tratamiento registrado."

    context = {
        'historial_citas': citas_completadas  # Mantiene el nombre exacto de tu variable HTML
    }
    return render(request, 'appvet/cliente/historial.html', context)

@login_required(login_url='login')
def cliente_configuracion(request):
    # Pasamos request.user directo como 'usuario' y agregamos el title para el header
    context = {
        'title': 'Configuración de Cuenta',
        'usuario': request.user
    }
    return render(request, 'appvet/cliente/configuracion.html', context)


@login_required(login_url='login')
def actualizar_configuracion(request):
    from django.contrib import messages
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        
        usuario = request.user
        usuario.first_name = nombre
        # Guardamos el teléfono en last_name para no romper el modelo nativo de auth_user
        usuario.last_name = telefono 
        usuario.save()
        
        messages.success(request, "Tus datos personales han sido actualizados con éxito.")
        return redirect('cliente_configuracion')
        
    messages.error(request, "No se pudieron procesar los cambios.")
    return redirect('cliente_configuracion')


@login_required(login_url='login')
def cambiar_password(request):
    from django.contrib import messages
    if request.method == 'POST':
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        
        usuario = request.user
        if usuario.check_password(current_password):
            usuario.set_password(new_password)
            usuario.save()
            
            # Sincroniza la sesión para evitar que el usuario se desloguee solo
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, usuario)
            
            messages.success(request, "Contraseña actualizada correctamente.")
        else:
            messages.error(request, "La contraseña actual es incorrecta o la nueva no cumple los requisitos.")
            
    return redirect('cliente_configuracion')















#VETERINARIO

# ===============================================================
# PORTAL DEL VETERINARIO (MÓDULO MÉDICO)
# ===============================================================

@login_required
def veterinario_inicio(request):
    fecha_param = request.GET.get('fecha')
    vista = request.GET.get('vista', 'Dia')

    hoy = timezone.now().date()
    
    # Resolver Fecha Base (Equivalente al DateTime Base = fecha ?? DateTime.Today)
    if fecha_param:
        try:
            fecha_base = datetime.strptime(fecha_param, '%Y-%m-%d').date()
        except ValueError:
            fecha_base = hoy
    else:
        fecha_base = hoy


    rango_horas = list(range(8, 20)) 


    citas_query = Cita.objects.select_related(
        'mascota',
        'mascota__usuario',
        'veterinario'
    ).filter(
        veterinario__usuario_id=request.user.username
    ).exclude(
        estado='Cancelada'
    )


    if vista == "Semana":

        diff = (fecha_base.weekday() - 0) % 7
        lunes = fecha_base - timedelta(days=diff)
        domingo = lunes + timedelta(days=7)
        
        citas_query = citas_query.filter(fecha__gte=lunes, fecha__lt=domingo)
        
        dias_mostrados = [lunes + timedelta(days=i) for i in range(7)]
        ancho_columna = 100 / 7
        
        fecha_anterior = (fecha_base - timedelta(days=7)).strftime('%Y-%m-%d')
        fecha_siguiente = (fecha_base + timedelta(days=7)).strftime('%Y-%m-%d')
        inicio_semana = lunes
        fin_semana = lunes + timedelta(days=6)
    else:
        citas_query = citas_query.filter(fecha=fecha_base)
        dias_mostrados = [fecha_base]
        ancho_columna = 100
        
        fecha_anterior = (fecha_base - timedelta(days=1)).strftime('%Y-%m-%d')
        fecha_siguiente = (fecha_base + timedelta(days=1)).strftime('%Y-%m-%d')
        inicio_semana = None
        fin_semana = None


    citas_procesadas = []

    for cita in citas_query:

        hora_int = 8
        try:
            # Limpiamos caracteres comunes por si guardas "09:00" o "9:00"
            hora_limpia = ''.join(c for c in cita.horario.split(':')[0] if c.isdigit())
            if hora_limpia:
                hora_int = int(hora_limpia)
        except Exception:
            pass


        desfase_horas = hora_int - 8
        if desfase_horas < 0: 
            desfase_horas = 0
            
        top_px = desfase_horas * 60
        
        # Manejo de minutos ("10:30" -> baja 30px más)
        if ":" in cita.horario:
            try:
                minutos_str = ''.join(c for c in cita.horario.split(':')[1] if c.isdigit())[:2]
                if minutos_str:
                    minutos_int = int(minutos_str)
                    top_px += int(minutos_int * (60 / 60))
            except Exception:
                pass

        # Configuración de colores según la prioridad
        color_prioridad = "#2c8a93" # Por defecto info / vet-primary
        if cita.prioridad == "Alta" or cita.es_emergencia:
            color_prioridad = "#dc3545" # Rojo danger
        elif cita.prioridad == "Media":
            color_prioridad = "#ffc107" # Amarillo warning


        citas_procesadas.append({
            'id': cita.id,
            'fecha_dt': cita.fecha,
            'mascota_nombre': cita.mascota.nombre,
            'horario': cita.horario,
            'estado': cita.estado,
            'top_px': top_px,
            'color_prioridad': color_prioridad
        })

    context = {
        'citas': citas_procesadas,
        'fecha_actual': fecha_base,
        'hoy_str': hoy.strftime('%Y-%m-%d'),
        'fecha_anterior': fecha_anterior,
        'fecha_siguiente': fecha_siguiente,
        'vista': vista,
        'rango_horas': rango_horas,
        'dias_mostrados': dias_mostrados,
        'ancho_columna': ancho_columna,
        'inicio_semana': inicio_semana,
        'fin_semana': fin_semana
    }
    return render(request, 'appvet/veterinario/inicio_veterinario.html', context)


@login_required
def historial_pacientes(request):
    search_string = request.GET.get('searchString')
    query = HistoriaClinica.objects.select_related('mascota', 'mascota__usuario')

    if search_string:
        query = query.filter(
            Q(mascota__nombre__icontains=search_string) |
            Q(mascota__usuario__first_name__icontains=search_string) |
            Q(mascota__usuario__username__icontains=search_string)
        )

    historial = query.order_by('-fecha_atencion')
    return render(request, 'appvet/veterinario/historialPaciente.html', {'historial': historial})


@login_required
def mis_consultas(request):
    mis_atenciones = HistoriaClinica.objects.select_related(
        'mascota',
        'mascota__usuario',
        'cita',
        'cita__veterinario'
    ).filter(
        cita__veterinario__usuario_id=request.user.username
    ).order_by('-fecha_atencion')

    return render(request, 'appvet/veterinario/misConsultas.html', {'consultas': mis_atenciones})


@login_required
def detalle_paciente(request, id):
    mascota = get_object_or_404(
        Mascota.objects.select_related('usuario').prefetch_related('historias_clinicas'),
        id=id
    )
    historias_ordenadas = mascota.historias_clinicas.all().order_by('-fecha_atencion')

    context = { 'mascota': mascota, 'historias': historias_ordenadas }

    return render(request, 'appvet/veterinario/detallesPaciente.html', context)


@login_required
def finalizar_consulta(request, cita_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")

    cita = get_object_or_404(Cita.objects.select_related('mascota', 'veterinario'), id=cita_id)

    if not cita.veterinario or cita.veterinario.usuario_id != request.user.username:
        return HttpResponseForbidden("No tienes permisos para modificar esta consulta.")

    diagnostico = request.POST.get('diagnostico')
    tratamiento = request.POST.get('tratamiento')
    proxima_cita_str = request.POST.get('proximaCitaSugerida')

    proxima_cita = None
    if proxima_cita_str:
        try:
            proxima_cita = datetime.strptime(proxima_cita_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    v_nombre = cita.veterinario.nombre if cita.veterinario else "Veterinario"

    HistoriaClinica.objects.create(
        mascota=cita.mascota,
        cita=cita,
        fecha_atencion=timezone.now(),
        diagnostico=diagnostico,
        tratamiento=tratamiento,
        veterinario_nombre=v_nombre,
        proxima_cita_sugerida=proxima_cita
    )

    cita.estado = 'Completada'
    cita.save()

    messages.success(request, "La consulta médica ha sido registrada con éxito.")
    return redirect('veterinario_inicio')