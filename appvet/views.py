from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Mascota, Cita, Veterinario, HistoriaClinica
from django.utils import timezone
from django.db import connection

# ==========================================
# VISTAS PÚBLICAS (CLIENTE)
# ==========================================

def home(request):
    return render(request, 'aplicacioncurso/cliente/home.html')

def quienes_somos(request):
    return render(request, 'aplicacioncurso/cliente/quienes_somos.html')

def ofertas(request):
    return render(request, 'aplicacioncurso/cliente/ofertas.html')

# ==========================================
# VISTAS DE ADMINISTRADOR
# ==========================================

def dashboard_admin(request):
    # Consultas reales a la base de datos
    hoy = timezone.now().date()
    
    context = {
        'citas_hoy': Cita.objects.filter(fecha=hoy).count(),
        'citas_pendientes': Cita.objects.filter(estado='Pendiente').count(),
        'total_mascotas': Mascota.objects.count(),
        'app_activa': True,  # Lógica de servidor
        'db_online': connection.ensure_connection() is None, # Verifica si hay conexión real
    }
    return render(request, 'aplicacioncurso/admin/dashboard_admin.html', context)

def gestion_citas(request):
    # Traemos todas las citas con select_related para optimizar la carga de mascotas
    citas = Cita.objects.all().select_related('mascota').order_by('-fecha')
    veterinarios = Veterinario.objects.filter(esta_activo=True)
    
    return render(request, 'aplicacioncurso/admin/gestion_citas.html', {
        'citas': citas,
        'veterinarios': veterinarios
    })

def lista_veterinarios(request):
    veterinarios = Veterinario.objects.all().order_by('-esta_activo', 'nombre')
    return render(request, 'aplicacioncurso/admin/lista_veterinarios.html', {
        'veterinarios': veterinarios
    })

def pacientes_por_volver(request):
    # Filtramos historias clínicas que tienen una fecha de próxima cita sugerida
    historias = HistoriaClinica.objects.filter(
        proxima_cita_sugerida__isnull=False
    ).select_related('mascota', 'mascota__usuario').order_by('proxima_cita_sugerida')
    
    return render(request, 'aplicacioncurso/admin/pacientes_porvolver.html', {
        'historias': historias
    })

# ==========================================
# LÓGICA DE ACCIONES (POST)
# ==========================================

def asignar_veterinario(request):
    if request.method == 'POST':
        cita_id = request.POST.get('cita_id')
        vete_id = request.POST.get('veterinario_id')
        
        cita = get_object_or_404(Cita, id=cita_id)
        vete = get_object_or_404(Veterinario, id=vete_id)
        
        cita.veterinario = vete
        cita.estado = 'Confirmada'
        cita.save()
        
        messages.success(request, f"Cita de {cita.mascota.nombre} asignada al Dr. {vete.nombre}")
        return redirect('gestion_citas')

def eliminar_cita(request, cita_id):
    if request.method == 'POST':
        cita = get_object_or_404(Cita, id=cita_id)
        nombre_mascota = cita.mascota.nombre
        cita.delete()
        messages.warning(request, f"La cita de {nombre_mascota} ha sido eliminada.")
        return redirect('gestion_citas')