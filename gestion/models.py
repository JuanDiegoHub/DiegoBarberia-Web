from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Sede(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    # Relación uno a uno con el modelo de Usuario de Django
    administrador = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sede_administrada'
    )

    def __str__(self):
        return self.nombre

class Barbero(models.Model):
    # Definimos las opciones para el estado
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('vacaciones', 'De Vacaciones'),
        ('inactivo', 'Inactivo'),
    ]
    user = models.OneToOneField('auth.User', on_delete=models.SET_NULL, null=True, blank=True)  # Relación opcional con User
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, null=True, blank=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='barberos')
    imagen = models.ImageField(upload_to='barberos/', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.IntegerField(default=30)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='servicios')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

class Cita(models.Model):
    # Estados de la cita
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente de Verificación'),
        ('Confirmada', 'Confirmada (Esperando Cliente)'),
        ('En_Atencion', 'Cliente en Barbería'),
        ('Completada', 'Servicio Finalizado'),
        ('No_Asistio', 'No Asistió'),
        ('Cancelada', 'Cancelada'),
    ]

    # Validador para números de teléfono (formato internacional opcional)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número debe tener entre 9 y 15 dígitos."
    )

    telefono = models.CharField(validators=[phone_regex], max_length=17)
    cliente_nombre = models.CharField(max_length=100, default='Cliente')
    # Relación con el Barbero que ya creamos
    barbero = models.ForeignKey('Barbero', on_delete=models.CASCADE, related_name='citas')
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    
    # Campos de control
    codigo_verificacion = models.CharField(max_length=6, blank=True, null=True)
    intentos_verificacion = models.IntegerField(default=0)
    verificado = models.BooleanField(default=False)
    recordatorio_enviado = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    hora_llegada = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordenar por fecha y hora por defecto
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"Cita {self.id} - {self.telefono} con {self.barbero.nombre}"

class HorarioSede(models.Model):
    DIA_CHOICES = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ]
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIA_CHOICES)
    hora_apertura = models.TimeField(default='08:00')
    hora_cierre = models.TimeField(default='20:00')
    cerrado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sede', 'dia_semana')
        ordering = ['dia_semana']

    def __str__(self):
        estado = "Cerrado" if self.cerrado else f"{self.hora_apertura} - {self.hora_cierre}"
        return f"{self.sede.nombre} - {self.get_dia_semana_display()}: {estado}"

class HorarioBarbero(models.Model):
    DIA_CHOICES = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ]
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIA_CHOICES)
    hora_entrada = models.TimeField(default='08:00')
    hora_salida = models.TimeField(default='20:00')
    inicio_almuerzo = models.TimeField(null=True, blank=True)
    fin_almuerzo = models.TimeField(null=True, blank=True)
    dia_descanso = models.BooleanField(default=False)

    class Meta:
        unique_together = ('barbero', 'dia_semana')
        ordering = ['dia_semana']

    def __str__(self):
        estado = "Descanso" if self.dia_descanso else f"{self.hora_entrada} - {self.hora_salida}"
        return f"{self.barbero.nombre} - {self.get_dia_semana_display()}: {estado}"