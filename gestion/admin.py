from django.contrib import admin
from .models import Sede, Barbero, Servicio

@admin.register(Barbero) # Usamos un decorador para configurar el panel
class BarberoAdmin(admin.ModelAdmin):
    # Campos que se verán en la lista principal del admin
    list_display = ('nombre', 'apellido', 'user', 'sede', 'estado') 
    # Campos que se verán dentro del formulario del admin
    fields = ('user', 'nombre', 'apellido', 'especialidad', 'sede', 'imagen', 'estado')

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'duracion_minutos', 'sede', 'activo')
    list_filter = ('sede', 'activo')

admin.site.register(Sede)