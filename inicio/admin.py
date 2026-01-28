from django.contrib import admin
from .models import Barbero, Servicio# Importamos el modelo que creamos antes

@admin.register(Barbero)
class BarberoAdmin(admin.ModelAdmin):
    # Solo mostramos nombre y especialidad en la lista
    list_display = ('nombre', 'especialidad')
    search_fields = ('nombre',)


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    list_editable = ('precio',) # Permite cambiar precios rápido sin entrar al perfil