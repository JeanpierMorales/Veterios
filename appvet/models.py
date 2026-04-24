from django.db import models
from django.contrib.auth.models import User
from datetime import date

# 1. Veterinario (Mismo que C#)
class Veterinario(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    usuario_id = models.CharField(max_length=100, null=True, blank=True)
    esta_activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# 2. Mascota (Incluyendo el cálculo de edad de C#)
class Mascota(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=50)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField(default=date.today)
    sexo = models.CharField(max_length=20, null=True, blank=True) # Macho/Hembra
    foto = models.ImageField(upload_to='mascotas/', null=True, blank=True)

    @property
    def edad(self):
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (self.fecha_nacimiento.month, self.fecha_nacimiento.day) > (hoy.month, hoy.day):
            edad -= 1
        return edad

    def __str__(self):
        return self.nombre

# 3. Cita (Con todos los campos de tu clase C#)
class Cita(models.Model):
    PRIORIDAD_CHOICES = [('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')]
    ESTADOS_CHOICES = [('Pendiente', 'Pendiente'), ('Confirmada', 'Confirmada'), ('Completada', 'Completada'), ('Cancelada', 'Cancelada')]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, blank=True)
    
    servicio = models.CharField(max_length=100)
    fecha = models.DateField()
    horario = models.CharField(max_length=50) # Ejemplo: "10:00 AM"
    prioridad = models.CharField(max_length=10)
    observaciones = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='Pendiente')
    es_emergencia = models.BooleanField(default=False)
    
    # Campos para notas médicas dentro de la cita
    diagnostico = models.TextField(null=True, blank=True)
    tratamiento = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Cita {self.mascota.nombre} - {self.fecha}"

# 4. Historia Clínica (Mapeado de C#)
class HistoriaClinica(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='historias_clinicas')
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True, blank=True)
    
    fecha_atencion = models.DateTimeField(auto_now_add=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    veterinario_nombre = models.CharField(max_length=100) # Quién atendió
    proxima_cita_sugerida = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Historia {self.mascota.nombre} - {self.fecha_atencion.date()}"