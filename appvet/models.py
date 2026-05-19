from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Veterinario(models.Model):
    nombre = models.CharField(max_length=150)
    especialidad = models.CharField(max_length=100)
    usuario_id = models.CharField(max_length=100, null=True, blank=True)
    esta_activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Mascota(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=100)
    raza = models.CharField(max_length=100)
    especie = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(default=date.today)
    sexo = models.CharField(max_length=20, null=True, blank=True) # Macho / Hembra

    @property
    def edad(self):
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (self.fecha_nacimiento.month, self.fecha_nacimiento.day) > (hoy.month, hoy.day):
            edad -= 1
        return edad

    def __str__(self):
        return self.nombre

class Cita(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='citas')
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas')
    
    servicio = models.CharField(max_length=150)
    fecha = models.DateField()
    horario = models.CharField(max_length=50)
    prioridad = models.CharField(max_length=20, default='Baja')
    observaciones = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=50, default='Pendiente')
    es_emergencia = models.BooleanField(default=False)
    
    # Notas médicas integradas de la cita
    diagnostico = models.TextField(null=True, blank=True)
    tratamiento = models.TextField(null=True, blank=True)
    nombre_veterinario = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Cita {self.id} - {self.mascota.nombre}"

class HistoriaClinica(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='historias_clinicas')
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True, blank=True, related_name='historias_clinicas')
    
    fecha_atencion = models.DateTimeField(auto_now_add=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    veterinario_nombre = models.CharField(max_length=150)
    proxima_cita_sugerida = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Historia {self.id} - {self.mascota.nombre}"