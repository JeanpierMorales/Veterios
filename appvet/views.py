from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import Mascota, Cita, Veterinario, HistoriaClinica
from django.utils import timezone
from django.db import connection

# ==========================================
# VISTAS PÚBLICAS (CLIENTE)
# ==========================================

def login_view(request):
    # Aquí irá la lógica de POST para iniciar sesión
    return render(request, 'appvet/account/login.html')

def quienes_somos(request):
    # Esta es tu página de aterrizaje principal
    return render(request, 'appvet/account/quienes_somos.html')

def ofertas(request):
    return render(request, 'appvet/account/ofertas.html')


def register_view(request):
    # Por ahora solo redirecciona, luego pondremos la lógica real
    return redirect('login')

def logout_view(request):
    auth_logout(request)
    return redirect('login')


# ==========================================
# VISTAS DE ADMINISTRADOR
# ==========================================

def dashboard_admin(request):
    hoy = timezone.now().date()
    
    # Aquí está tu "DashboardViewModel" de C#
    context = {
        'citas_hoy': Cita.objects.filter(fecha=hoy).count(),
        'citas_pendientes': Cita.objects.filter(estado='Pendiente').count(),
        'total_mascotas': Mascota.objects.count(),
        'app_activa': True,
        'db_online': True, # Podríamos verificar la conexión real aquí
    }
    return render(request, 'appvet/admin/dashboard_admin.html', context)

def gestion_citas(request):
    citas = Cita.objects.all().select_related('mascota').order_by('-fecha')
    veterinarios = Veterinario.objects.filter(esta_activo=True)
    return render(request, 'appvet/admin/gestion_citas.html', {'citas': citas, 'veterinarios': veterinarios})

# ... Mantén las demás funciones (asignar_veterinario, eliminar_cita, etc.)
def lista_veterinarios(request):
    veterinarios = Veterinario.objects.all().order_by('-esta_activo', 'nombre')
    return render(request, 'appvet/admin/lista_veterinarios.html', {
        'veterinarios': veterinarios
    })

def pacientes_por_volver(request):
    # Filtramos historias clínicas que tienen una fecha de próxima cita sugerida
    historias = HistoriaClinica.objects.filter(
        proxima_cita_sugerida__isnull=False
    ).select_related('mascota', 'mascota__usuario').order_by('proxima_cita_sugerida')
    
    return render(request, 'appvet/admin/pacientes_porvolver.html', {
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