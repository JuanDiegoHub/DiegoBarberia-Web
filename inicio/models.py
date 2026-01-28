from django.db import models

from django.db import models

class Barbero(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    # blank=True permite que el formulario del admin lo acepte vacío
    # null=True permite que la base de datos guarde un valor nulo
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad", null=True, blank=True)
    foto = models.ImageField(upload_to='barberos/', verbose_name="Foto de Perfil")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Barbero"
        verbose_name_plural = "Nuestros Barberos"

class Servicio(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    precio = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Precio") # Usamos 0 decimales para moneda local

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"