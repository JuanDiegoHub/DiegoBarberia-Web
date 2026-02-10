from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # <--- Esta es la importación que faltaba
from .models import sede, Usuario

# Registro básico de la Sede
admin.site.register(sede)

# Registro del Usuario personalizado
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin): # <--- Aquí usamos UserAdmin en lugar de ModelAdmin
    list_display = ('username', 'email', 'role', 'sede', 'is_staff')
    list_filter = ('role', 'sede')
    
    # Agregamos nuestros campos personalizados a los que ya trae Django
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Barbería', {'fields': ('role', 'sede')}),
    )
    # También los agregamos al formulario de creación (opcional pero recomendado)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Barbería', {'fields': ('role', 'sede')}),
    )