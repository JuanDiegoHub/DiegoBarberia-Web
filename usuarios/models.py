from django.db import models
from django.contrib.auth.models import AbstractUser

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

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"