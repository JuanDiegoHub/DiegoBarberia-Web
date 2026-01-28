from django.shortcuts import render
from .models import Barbero, Servicio # Importamos tu modelo

def home(request): # Obtenemos todos los barberos de la base de datos
    barberos = Barbero.objects.all() # Los pasamos al HTML en un diccionario llamado 'context'
    return render(request, 'inicio/index.html', {'barberos': barberos})

def home(request):
    barberos = Barbero.objects.all()
    servicios = Servicio.objects.all() # Traemos los servicios
    return render(request, 'inicio/index.html', {
        'barberos': barberos,
        'servicios': servicios
    })