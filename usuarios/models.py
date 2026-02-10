from django.db import models
from django.contrib.auth.models import AbstractUser

class sede(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
    
class Usuario(AbstractUser):
    ADMIN = 'admin'
    BARBERO = 'barbero'

    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (BARBERO, 'Barbero'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=BARBERO,
    )

    sede = models.ForeignKey(
        sede,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='barberos'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"